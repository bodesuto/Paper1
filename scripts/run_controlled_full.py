"""Controlled Full Run Script: One strategy at a time with 100-row probe.

WORKFLOW:
  Step 1: Probe run (100 rows) for the target strategy → review cost report.
  Step 2: If cost/accuracy looks good → continue with full 10,000 rows.
  Step 3: Move to next strategy only when current one is complete.

Usage:
    # Step 1: Probe one strategy (safe, cheap)
    python scripts/run_controlled_full.py --strategy heuristic --probe

    # Step 2: Full run for that strategy (after reviewing probe output)
    python scripts/run_controlled_full.py --strategy heuristic

    # Full pipeline for all strategies (runs probe first, then auto-continues)
    python scripts/run_controlled_full.py --all --probe-first

    # Reflexion agent
    python scripts/run_controlled_full.py --agent reflexion --strategy heuristic
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from common.env_setup import apply_env
from common.config import DATA_PATH, TRAVERSAL_POLICY_PATH

apply_env()

# Ordered list of strategies from cheapest → most expensive / complex
STRATEGY_ORDER = [
    "heuristic",
    "vector_rag",
    "graph_rag",
    "ontology_only",
    "traversal_only",
    "learned",
    "full",
]

PROBE_ROWS = 100


def _get_test_func(agent: str, mode: str = "dual_memory"):
    if agent == "react" and mode == "dual_memory":
        from eval.test.react_test import test_dual_memory
        return test_dual_memory
    if agent == "reflexion" and mode == "dual_memory":
        from eval.test.reflexion_test import test_dual_memory
        return test_dual_memory
    if agent == "react" and mode == "baseline":
        from eval.test.react_test import test
        return test
    if agent == "reflexion" and mode == "baseline":
        from eval.test.reflexion_test import test
        return test
    raise ValueError(f"Unknown agent/mode: {agent}/{mode}")


def run_strategy(
    agent: str,
    strategy: str,
    data_path: str,
    output_dir: Path,
    row_limit: int | None = None,
) -> bool:
    """Run one strategy. Returns True on success."""
    suffix = f"_probe{row_limit}" if row_limit else "_full"
    out_file = output_dir / f"{agent}_{strategy}{suffix}.csv"

    print(f"\n{'='*65}")
    print(f"  STRATEGY: {strategy.upper()}  |  AGENT: {agent.upper()}")
    print(f"  Rows:     {row_limit or 'ALL'}")
    print(f"  Output:   {out_file.name}")
    print(f"{'='*65}")

    if strategy == "full" and not Path(TRAVERSAL_POLICY_PATH).exists():
        print(f"  [SKIP] strategy=full requires trained policy at {TRAVERSAL_POLICY_PATH}")
        print(f"         Run: python scripts/run_fit_traversal_policy.py first.")
        return False

    test_func = _get_test_func(agent)
    start = time.perf_counter()
    try:
        test_func(
            data_path=data_path,
            output_path=out_file,
            retrieval_strategy=strategy,
            row_limit=row_limit,
        )
        elapsed = time.perf_counter() - start
        print(f"\n  ✅ Strategy '{strategy}' completed in {elapsed/60:.1f} min.")
        return True
    except Exception as e:
        import traceback
        elapsed = time.perf_counter() - start
        print(f"\n  ❌ Strategy '{strategy}' FAILED after {elapsed/60:.1f} min: {e}")
        traceback.print_exc()
        return False


def print_probe_gate(strategy: str, probe_file: Path) -> bool:
    """Read probe CSV and print cost/accuracy summary. Return True to continue."""
    try:
        import pandas as pd
        df = pd.read_csv(probe_file)
        n = len(df)
        em = df["exact_match"].sum() if "exact_match" in df.columns else "N/A"
        em_eval = df["exact_match_eval_success"].sum() if "exact_match_eval_success" in df.columns else "N/A"
        cost = df["cost_usd"].sum() if "cost_usd" in df.columns else 0.0
        projected = cost / n * 10_000 if n > 0 else 0

        print(f"\n{'─'*65}")
        print(f"  📊 PROBE RESULT: strategy={strategy}")
        print(f"     Rows evaluated:    {n}")
        print(f"     Exact Match (sub): {em}/{n}  ({100*em/n:.1f}%)" if isinstance(em, (int, float)) else f"     Exact Match:       {em}")
        print(f"     Exact Match (LLM): {em_eval}")
        print(f"     Probe cost (est):  ${cost:.4f}")
        print(f"     Proj. 10k cost:    ${projected:.2f}")
        print(f"{'─'*65}")
        print(f"\n  ⚠️  Review the numbers above. To continue full run:")
        print(f"     python scripts/run_controlled_full.py --strategy {strategy}")
    except Exception as e:
        print(f"  [probe review failed: {e}]")
    return True


def main():
    parser = argparse.ArgumentParser(description="Controlled full run: one strategy at a time with probe gate.")
    parser.add_argument("--agent", choices=["react", "reflexion"], default="react")
    parser.add_argument("--strategy", choices=STRATEGY_ORDER + ["all"], default="heuristic")
    parser.add_argument("--data-path", default=os.path.join(DATA_PATH, "hard_bridge_500_validation.csv"),
                        help="Path to the dataset CSV (1000-10000 rows).")
    parser.add_argument("--output-dir", default=os.path.join(DATA_PATH, "ablations"))
    parser.add_argument("--probe", action="store_true",
                        help=f"Run only first {PROBE_ROWS} rows as a cost probe.")
    parser.add_argument("--probe-first", action="store_true",
                        help="When --all: run probe for each strategy before full run.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Override row limit (overrides --probe).")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    strategies = STRATEGY_ORDER if args.strategy == "all" else [args.strategy]
    row_limit = args.limit if args.limit else (PROBE_ROWS if args.probe else None)

    for strategy in strategies:
        if args.probe_first and not args.probe:
            # Run probe first, then full
            probe_file = output_dir / f"{args.agent}_{strategy}_probe{PROBE_ROWS}.csv"
            run_strategy(args.agent, strategy, args.data_path, output_dir, row_limit=PROBE_ROWS)
            print_probe_gate(strategy, probe_file)
            print(f"\n  Continuing to FULL run for strategy={strategy} ...")
            time.sleep(3)
            run_strategy(args.agent, strategy, args.data_path, output_dir, row_limit=None)
        else:
            run_strategy(args.agent, strategy, args.data_path, output_dir, row_limit=row_limit)

        # Inter-strategy cooldown to let API rate limits reset
        if len(strategies) > 1:
            print(f"\n  [Cooldown] Waiting 30s before next strategy ...")
            time.sleep(30)

    print("\n\n🎉 All requested strategies completed.")
    print(f"   Results saved in: {output_dir}")


if __name__ == "__main__":
    main()
