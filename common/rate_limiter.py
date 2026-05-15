"""Rate Limiter & Cost Monitor for DualMemoryKG Full Run.

Prevents API DDOS / quota exhaustion when calling Gemini at scale.

Features:
- Token-bucket rate limiter (max N calls/minute per strategy)
- Inter-call delay (sleep between API calls)
- Rolling cost tracker with early-stop on budget breach
- 100-row checkpoint reporter

Usage:
    from common.rate_limiter import RateLimiter, CostMonitor

    limiter = RateLimiter(calls_per_minute=15, min_delay_s=4.0)
    monitor = CostMonitor(budget_usd=10.0, checkpoint_every=100)

    # Before each API call:
    limiter.wait()

    # After each row:
    monitor.record(row_index=i, cost_usd=cb.total_cost, tokens=cb.total_tokens)
"""
from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from typing import Callable


# ---------------------------------------------------------------------------
# Rate Limiter (Token Bucket)
# ---------------------------------------------------------------------------

class RateLimiter:
    """Thread-safe token-bucket rate limiter.

    Args:
        calls_per_minute: Max LLM API calls allowed per minute.
                          Gemini Flash free tier: ~15 RPM is safe.
        min_delay_s: Minimum seconds to sleep between calls regardless of bucket.
                     Set to 4.0 for Gemini Flash to avoid 429s.
    """

    def __init__(self, calls_per_minute: int = 12, min_delay_s: float = 5.0):
        self.calls_per_minute = calls_per_minute
        self.min_delay_s = min_delay_s
        self._lock = threading.Lock()
        self._call_times: list[float] = []
        self._last_call_time: float = 0.0

    def wait(self) -> None:
        """Block until it is safe to make the next API call."""
        with self._lock:
            now = time.monotonic()

            # Enforce minimum inter-call delay
            elapsed_since_last = now - self._last_call_time
            if elapsed_since_last < self.min_delay_s:
                sleep_for = self.min_delay_s - elapsed_since_last
                time.sleep(sleep_for)
                now = time.monotonic()

            # Enforce calls-per-minute window
            window_start = now - 60.0
            self._call_times = [t for t in self._call_times if t >= window_start]

            if len(self._call_times) >= self.calls_per_minute:
                # Wait until oldest call falls out of 60-second window
                oldest = self._call_times[0]
                wait_until = oldest + 60.0
                sleep_for = max(0, wait_until - now)
                if sleep_for > 0:
                    print(f"  [RateLimiter] RPM limit reached. Sleeping {sleep_for:.1f}s ...")
                    time.sleep(sleep_for)
                    now = time.monotonic()
                self._call_times = [t for t in self._call_times if t >= now - 60.0]

            self._call_times.append(now)
            self._last_call_time = now


# ---------------------------------------------------------------------------
# Cost Monitor
# ---------------------------------------------------------------------------

@dataclass
class RowStats:
    index: int
    cost_usd: float
    total_tokens: int
    exact_match: bool


class CostMonitor:
    """Tracks cumulative cost and logs a checkpoint every N rows.

    Args:
        budget_usd: Hard stop — raises BudgetExceededError if exceeded.
                    Set to None to disable.
        checkpoint_every: Print a cost report every N rows.
        on_checkpoint: Optional callback(stats_dict) for custom logging.
    """

    def __init__(
        self,
        budget_usd: float | None = 5.0,
        checkpoint_every: int = 100,
        on_checkpoint: Callable[[dict], None] | None = None,
    ):
        self.budget_usd = budget_usd
        self.checkpoint_every = checkpoint_every
        self.on_checkpoint = on_checkpoint

        self._rows: list[RowStats] = []
        self._total_cost: float = 0.0
        self._total_tokens: int = 0
        self._exact_matches: int = 0

    @property
    def total_cost(self) -> float:
        return self._total_cost

    @property
    def rows_processed(self) -> int:
        return len(self._rows)

    def record(
        self,
        row_index: int,
        cost_usd: float | None,
        tokens: int | None,
        exact_match: bool = False,
    ) -> None:
        """Record stats for one completed row."""
        safe_cost = float(cost_usd or 0.0)
        safe_tokens = int(tokens or 0)

        self._rows.append(RowStats(row_index, safe_cost, safe_tokens, exact_match))
        self._total_cost += safe_cost
        self._total_tokens += safe_tokens
        if exact_match:
            self._exact_matches += 1

        n = len(self._rows)
        if n % self.checkpoint_every == 0:
            self._print_checkpoint()

        if self.budget_usd is not None and self._total_cost > self.budget_usd:
            raise BudgetExceededError(
                f"Budget of ${self.budget_usd:.2f} exceeded after {n} rows "
                f"(spent: ${self._total_cost:.4f})"
            )

    def _print_checkpoint(self) -> None:
        n = len(self._rows)
        avg_cost = self._total_cost / n if n else 0
        avg_tokens = self._total_tokens / n if n else 0
        em_pct = 100.0 * self._exact_matches / n if n else 0
        projected_total = avg_cost * 10_000  # projected for 10k questions

        report = {
            "rows_done": n,
            "total_cost_usd": round(self._total_cost, 4),
            "avg_cost_per_row": round(avg_cost, 5),
            "avg_tokens_per_row": round(avg_tokens, 1),
            "exact_match_pct": round(em_pct, 2),
            "projected_10k_cost_usd": round(projected_total, 2),
        }

        print("\n" + "=" * 60)
        print(f"  📊 COST CHECKPOINT @ row {n}")
        print(f"  Total spent:          ${report['total_cost_usd']:.4f}")
        print(f"  Avg cost/row:         ${report['avg_cost_per_row']:.5f}")
        print(f"  Avg tokens/row:       {report['avg_tokens_per_row']:.0f}")
        print(f"  Exact Match so far:   {report['exact_match_pct']:.1f}%")
        print(f"  Projected 10k cost:   ${report['projected_10k_cost_usd']:.2f}")
        if self.budget_usd:
            remaining = self.budget_usd - self._total_cost
            print(f"  Budget remaining:     ${remaining:.4f}")
        print("=" * 60 + "\n")

        if self.on_checkpoint:
            self.on_checkpoint(report)

    def final_summary(self) -> dict:
        """Return final statistics dict."""
        n = len(self._rows)
        return {
            "total_rows": n,
            "total_cost_usd": round(self._total_cost, 4),
            "total_tokens": self._total_tokens,
            "exact_match_count": self._exact_matches,
            "exact_match_pct": round(100.0 * self._exact_matches / n, 2) if n else 0,
            "avg_cost_per_row": round(self._total_cost / n, 5) if n else 0,
        }


class BudgetExceededError(RuntimeError):
    """Raised when cumulative API cost exceeds the configured budget."""
    pass
