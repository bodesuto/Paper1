from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def _method_name(path_value: str) -> str:
    stem = Path(str(path_value)).stem
    for prefix in ("react_", "reflexion_"):
        if stem.startswith(prefix):
            stem = stem[len(prefix):]
    return stem


def _safe_float(value, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def build_architecture_validity_report(
    summary_csv: str | Path,
    *,
    results_csv: str | Path | None = None,
    output_path: str | Path | None = None,
    error_output_path: str | Path | None = None,
) -> tuple[dict[str, object], pd.DataFrame | None]:
    summary_df = pd.read_csv(summary_csv)
    if "file" in summary_df.columns:
        summary_df["method"] = summary_df["file"].map(_method_name)
    elif "retrieval_strategy" in summary_df.columns:
        summary_df["method"] = summary_df["retrieval_strategy"]
    else:
        summary_df["method"] = [f"method_{idx}" for idx in range(len(summary_df))]

    method_rows = {
        str(row["method"]): row
        for _, row in summary_df.iterrows()
    }

    baseline = method_rows.get("baseline")
    ontology_only = method_rows.get("ontology_only")
    traversal_only = method_rows.get("traversal_only")
    learned = method_rows.get("learned")
    full = method_rows.get("full")
    strongest = full if full is not None else learned

    report: dict[str, object] = {
        "methods_available": sorted(method_rows.keys()),
        "protocol": {
            "has_baseline": baseline is not None,
            "has_ontology_ablation": ontology_only is not None,
            "has_traversal_ablation": traversal_only is not None,
            "has_learned_system": learned is not None or full is not None,
            "has_annotation_metrics": bool(
                "evidence_f1" in summary_df.columns and summary_df["evidence_f1"].notna().any()
            ),
            "has_support_set_metrics": bool(
                "support_set_best_f1" in summary_df.columns and summary_df["support_set_best_f1"].notna().any()
            ),
        },
        "mechanism_evidence": {},
        "error_decomposition": {},
    }

    if baseline is not None and ontology_only is not None:
        report["mechanism_evidence"]["ontology_delta_vs_baseline"] = {
            "exact_match_eval": _safe_float(ontology_only.get("exact_match_eval")) - _safe_float(baseline.get("exact_match_eval")),
            "path_grounding_precision": _safe_float(ontology_only.get("path_grounding_precision")) - _safe_float(baseline.get("path_grounding_precision")),
            "evidence_f1": _safe_float(ontology_only.get("evidence_f1")) - _safe_float(baseline.get("evidence_f1")),
        }

    if baseline is not None and traversal_only is not None:
        report["mechanism_evidence"]["traversal_delta_vs_baseline"] = {
            "exact_match_eval": _safe_float(traversal_only.get("exact_match_eval")) - _safe_float(baseline.get("exact_match_eval")),
            "path_grounding_precision": _safe_float(traversal_only.get("path_grounding_precision")) - _safe_float(baseline.get("path_grounding_precision")),
            "unsupported_reasoning_score": _safe_float(traversal_only.get("unsupported_reasoning_score")) - _safe_float(baseline.get("unsupported_reasoning_score")),
        }

    if baseline is not None and strongest is not None:
        report["mechanism_evidence"]["strongest_delta_vs_baseline"] = {
            "exact_match_eval": _safe_float(strongest.get("exact_match_eval")) - _safe_float(baseline.get("exact_match_eval")),
            "faithfulness_score": _safe_float(strongest.get("faithfulness_score")) - _safe_float(baseline.get("faithfulness_score")),
            "path_grounding_precision": _safe_float(strongest.get("path_grounding_precision")) - _safe_float(baseline.get("path_grounding_precision")),
            "evidence_f1": _safe_float(strongest.get("evidence_f1")) - _safe_float(baseline.get("evidence_f1")),
            "support_set_best_f1": _safe_float(strongest.get("support_set_best_f1")) - _safe_float(baseline.get("support_set_best_f1")),
            "contradiction_exposure_rate": _safe_float(strongest.get("contradiction_exposure_rate")) - _safe_float(baseline.get("contradiction_exposure_rate")),
        }

    error_df = None
    if results_csv is not None:
        result_df = pd.read_csv(results_csv)
        categorized_rows = []
        for row in result_df.to_dict(orient="records"):
            exact_match_eval = _safe_float(row.get("exact_match_eval"))
            unsupported = _safe_float(row.get("unsupported_reasoning_score"))
            path_grounding = _safe_float(row.get("path_grounding_precision"))
            evidence_sufficiency = _safe_float(row.get("evidence_sufficiency_rate"))
            contradiction = _safe_float(row.get("contradiction_exposure_rate"))
            evidence_f1 = _safe_float(row.get("evidence_f1"))
            support_set_f1 = _safe_float(row.get("support_set_best_f1"))

            failure_modes: list[str] = []
            if exact_match_eval < 0.5:
                failure_modes.append("answer_error")
            if unsupported >= 0.5:
                failure_modes.append("unsupported_reasoning")
            if path_grounding < 0.4:
                failure_modes.append("low_path_grounding")
            if evidence_sufficiency < 0.5:
                failure_modes.append("insufficient_evidence")
            if contradiction > 0.0:
                failure_modes.append("contradictory_evidence_selected")
            if evidence_f1 < 0.4 and "evidence_f1" in result_df.columns:
                failure_modes.append("wrong_evidence_set")
            if support_set_f1 < 0.4 and "support_set_best_f1" in result_df.columns:
                failure_modes.append("support_set_mismatch")
            if not failure_modes:
                failure_modes.append("grounded_success")

            categorized_rows.append(
                {
                    "index": row.get("index"),
                    "question": row.get("question"),
                    "exact_match_eval": exact_match_eval,
                    "unsupported_reasoning_score": unsupported,
                    "path_grounding_precision": path_grounding,
                    "evidence_sufficiency_rate": evidence_sufficiency,
                    "contradiction_exposure_rate": contradiction,
                    "evidence_f1": evidence_f1,
                    "support_set_best_f1": support_set_f1,
                    "failure_modes": "|".join(failure_modes),
                }
            )

        error_df = pd.DataFrame(categorized_rows)
        total = max(len(error_df), 1)
        mode_counts: dict[str, float] = {}
        for modes in error_df["failure_modes"]:
            for mode in str(modes).split("|"):
                mode_counts[mode] = mode_counts.get(mode, 0.0) + 1.0
        report["error_decomposition"] = {
            mode: count / total
            for mode, count in sorted(mode_counts.items())
        }

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)

    if error_output_path is not None and error_df is not None:
        error_output_path = Path(error_output_path)
        error_output_path.parent.mkdir(parents=True, exist_ok=True)
        error_df.to_csv(error_output_path, index=False)

    return report, error_df
