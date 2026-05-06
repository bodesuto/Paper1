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
    "support_set_best_precision",
    "support_set_best_recall",
    "support_set_best_f1",
    "support_set_best_jaccard",
    "support_set_exact_match",
    "contradiction_exposure_rate",
    "agent_latency_s",
    "total_latency_s",
    # Error Decomposition Columns (Q1 requirement)
    "error_ontology_mismatch",
    "error_traversal_suboptimality",
    "error_grounding_gap",
    "error_knowledge_deficiency",
    "error_reasoning_loop",
    "error_timeout",
]


def _merge_evidence_metrics(results_df: pd.DataFrame, evidence_df: pd.DataFrame | None) -> pd.DataFrame:
    if evidence_df is None or evidence_df.empty:
        return results_df

    key = None
    for candidate in ("index", "question"):
        if candidate in results_df.columns and candidate in evidence_df.columns:
            key = candidate
            break
    if key is None:
        return results_df

    evidence_cols = [column for column in SUMMARY_COLUMNS if column in evidence_df.columns]
    if not evidence_cols:
        return results_df

    merged = results_df.merge(
        evidence_df[[key, *evidence_cols]].drop_duplicates(subset=[key]),
        on=key,
        how="left",
        suffixes=("", "_evidence"),
    )
    for column in evidence_cols:
        evidence_column = f"{column}_evidence"
        if evidence_column not in merged.columns:
            continue
        if column in merged.columns:
            merged[column] = merged[column].fillna(merged[evidence_column])
        else:
            merged[column] = merged[evidence_column]
        merged = merged.drop(columns=[evidence_column])
    return merged


def summarize_result_csv(
    csv_path: str | Path,
    *,
    bootstrap_samples: int = BOOTSTRAP_SAMPLES,
    seed: int = 13,
    evidence_csv_path: str | Path | None = None,
) -> dict[str, float | str]:
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)
    if evidence_csv_path is not None:
        evidence_csv_path = Path(evidence_csv_path)
        if evidence_csv_path.exists():
            df = _merge_evidence_metrics(df, pd.read_csv(evidence_csv_path))
    summary: dict[str, float | str] = {"file": str(csv_path), "rows": float(len(df))}
    for column in SUMMARY_COLUMNS:
        summary.update(summarize_metric_column(df, column, bootstrap_samples=bootstrap_samples, seed=seed))
    if "retrieval_strategy" in df.columns and not df.empty:
        summary["retrieval_strategy"] = str(df["retrieval_strategy"].mode().iloc[0])
    if evidence_csv_path is not None:
        summary["evidence_file"] = str(evidence_csv_path)
    return summary


def summarize_many(
    csv_paths: list[str | Path],
    output_path: str | Path | None = None,
    *,
    bootstrap_samples: int = BOOTSTRAP_SAMPLES,
    reference_path: str | Path | None = None,
    evidence_csv_paths: list[str | Path] | None = None,
) -> pd.DataFrame:
    evidence_csv_paths = evidence_csv_paths or [None] * len(csv_paths)
    if len(evidence_csv_paths) != len(csv_paths):
        raise ValueError("evidence_csv_paths must be omitted or have the same length as csv_paths")

    rows = [
        summarize_result_csv(path, bootstrap_samples=bootstrap_samples, evidence_csv_path=evidence_path)
        for path, evidence_path in zip(csv_paths, evidence_csv_paths)
    ]
    if reference_path is not None:
        reference_path = Path(reference_path)
        ref_df = pd.read_csv(reference_path)
        ref_evidence_path = None
        if reference_path in map(Path, csv_paths):
            reference_index = list(map(Path, csv_paths)).index(reference_path)
            ref_evidence_path = evidence_csv_paths[reference_index]
        if ref_evidence_path is not None and Path(ref_evidence_path).exists():
            ref_df = _merge_evidence_metrics(ref_df, pd.read_csv(ref_evidence_path))

        for row, csv_path, evidence_path in zip(rows, csv_paths, evidence_csv_paths):
            target_df = pd.read_csv(csv_path)
            if evidence_path is not None and Path(evidence_path).exists():
                target_df = _merge_evidence_metrics(target_df, pd.read_csv(evidence_path))
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
