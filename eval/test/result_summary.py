from __future__ import annotations

from pathlib import Path

import pandas as pd

from common.config import BOOTSTRAP_SAMPLES
from eval.test.statistics import align_paired_metric, paired_bootstrap_delta_ci, summarize_metric_column


SUMMARY_COLUMNS = [
    "exact_match",
    "exact_match_eval",
    "answer_relevancy_score",
    "faithfulness_score",
    "ctx_precision_score",
    "unsupported_reasoning_score",
    "path_grounding_precision",
    "memory_selection_accuracy",
    "evidence_sufficiency_rate",
    "evidence_precision",
    "evidence_recall",
    "evidence_f1",
    "evidence_set_coverage",
    "contradiction_exposure_rate",
    "agent_latency_s",
    "total_latency_s",
]


def summarize_result_csv(
    csv_path: str | Path,
    *,
    bootstrap_samples: int = BOOTSTRAP_SAMPLES,
    seed: int = 13,
) -> dict[str, float | str]:
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)
    summary: dict[str, float | str] = {"file": str(csv_path), "rows": float(len(df))}
    for column in SUMMARY_COLUMNS:
        summary.update(summarize_metric_column(df, column, bootstrap_samples=bootstrap_samples, seed=seed))
    if "retrieval_strategy" in df.columns and not df.empty:
        summary["retrieval_strategy"] = str(df["retrieval_strategy"].mode().iloc[0])
    return summary


def summarize_many(
    csv_paths: list[str | Path],
    output_path: str | Path | None = None,
    *,
    bootstrap_samples: int = BOOTSTRAP_SAMPLES,
    reference_path: str | Path | None = None,
) -> pd.DataFrame:
    rows = [summarize_result_csv(path, bootstrap_samples=bootstrap_samples) for path in csv_paths]
    if reference_path is not None:
        reference_path = Path(reference_path)
        ref_df = pd.read_csv(reference_path)
        for row, csv_path in zip(rows, csv_paths):
            target_df = pd.read_csv(csv_path)
            for metric in SUMMARY_COLUMNS:
                if metric not in target_df.columns or metric not in ref_df.columns:
                    continue
                ref_values, tgt_values = align_paired_metric(ref_df, target_df, metric)
                delta, ci_low, ci_high = paired_bootstrap_delta_ci(
                    ref_values,
                    tgt_values,
                    samples=bootstrap_samples,
                )
                row[f"{metric}_delta_vs_reference"] = delta
                row[f"{metric}_delta_ci_low"] = ci_low
                row[f"{metric}_delta_ci_high"] = ci_high
            row["reference_file"] = str(reference_path)
    df = pd.DataFrame(rows)
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
    return df
