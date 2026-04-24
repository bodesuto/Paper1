from __future__ import annotations

import math
import random
from typing import Any

import pandas as pd


def _clean_numeric(series: pd.Series) -> list[float]:
    return [float(value) for value in series.dropna().tolist()]


def mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    mean_value = sum(values) / len(values)
    if len(values) == 1:
        return mean_value, 0.0
    variance = sum((value - mean_value) ** 2 for value in values) / (len(values) - 1)
    return mean_value, math.sqrt(max(variance, 0.0))


def bootstrap_mean_ci(
    values: list[float],
    *,
    samples: int = 1000,
    confidence: float = 0.95,
    seed: int = 13,
) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return values[0], values[0]
    rng = random.Random(seed)
    means: list[float] = []
    n = len(values)
    for _ in range(max(samples, 1)):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    alpha = max(0.0, min(1.0, (1.0 - confidence) / 2.0))
    low_idx = int(alpha * (len(means) - 1))
    high_idx = int((1.0 - alpha) * (len(means) - 1))
    return means[low_idx], means[high_idx]


def align_paired_metric(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    metric: str,
) -> tuple[list[float], list[float]]:
    key = None
    for candidate in ("index", "question"):
        if candidate in left_df.columns and candidate in right_df.columns:
            key = candidate
            break
    if key is None:
        left_values = _clean_numeric(left_df[metric]) if metric in left_df.columns else []
        right_values = _clean_numeric(right_df[metric]) if metric in right_df.columns else []
        n = min(len(left_values), len(right_values))
        return left_values[:n], right_values[:n]

    merged = left_df[[key, metric]].merge(
        right_df[[key, metric]],
        on=key,
        suffixes=("_left", "_right"),
        how="inner",
    )
    return _clean_numeric(merged[f"{metric}_left"]), _clean_numeric(merged[f"{metric}_right"])


def paired_bootstrap_delta_ci(
    left_values: list[float],
    right_values: list[float],
    *,
    samples: int = 1000,
    confidence: float = 0.95,
    seed: int = 13,
) -> tuple[float, float, float]:
    n = min(len(left_values), len(right_values))
    if n == 0:
        return 0.0, 0.0, 0.0
    deltas = [float(right_values[idx]) - float(left_values[idx]) for idx in range(n)]
    mean_delta = sum(deltas) / n
    if n == 1:
        return mean_delta, mean_delta, mean_delta

    rng = random.Random(seed)
    boot: list[float] = []
    for _ in range(max(samples, 1)):
        sampled = [deltas[rng.randrange(n)] for _ in range(n)]
        boot.append(sum(sampled) / n)
    boot.sort()
    alpha = max(0.0, min(1.0, (1.0 - confidence) / 2.0))
    low_idx = int(alpha * (len(boot) - 1))
    high_idx = int((1.0 - alpha) * (len(boot) - 1))
    return mean_delta, boot[low_idx], boot[high_idx]


def summarize_metric_column(
    df: pd.DataFrame,
    metric: str,
    *,
    bootstrap_samples: int = 1000,
    seed: int = 13,
) -> dict[str, Any]:
    if metric not in df.columns:
        return {}
    values = _clean_numeric(df[metric])
    mean_value, std_value = mean_std(values)
    ci_low, ci_high = bootstrap_mean_ci(values, samples=bootstrap_samples, seed=seed)
    return {
        metric: mean_value,
        f"{metric}_std": std_value,
        f"{metric}_ci_low": ci_low,
        f"{metric}_ci_high": ci_high,
    }
