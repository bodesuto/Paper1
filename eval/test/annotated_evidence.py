from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from eval.test.support_set_metrics import support_set_best_match


def _parse_json_field(value: Any, default):
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
        try:
            return json.loads(value)
        except Exception:
            return default
    return default


@dataclass
class EvidenceAnnotation:
    index: str
    question: str
    gold_answer: str = ""
    gold_evidence_node_ids: list[str] = field(default_factory=list)
    sufficient_evidence_sets: list[list[str]] = field(default_factory=list)
    contradiction_node_ids: list[str] = field(default_factory=list)
    annotation_status: str = "pending"
    notes: str = ""
    selected_retrieval_path: list[dict[str, Any]] = field(default_factory=list)
    candidate_retrieval_path: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_annotation_template(
    results_csv: str | Path,
    output_path: str | Path,
    *,
    limit: int | None = None,
) -> Path:
    results_csv = Path(results_csv)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(results_csv)
    if limit is not None:
        df = df.head(limit)

    records: list[dict[str, Any]] = []
    for row in df.to_dict(orient="records"):
        annotation = EvidenceAnnotation(
            index=str(row.get("index", row.get("id", ""))),
            question=str(row.get("question", "")),
            gold_answer=str(row.get("gold_answer", "")),
            selected_retrieval_path=_parse_json_field(row.get("retrieval_path"), []),
            candidate_retrieval_path=_parse_json_field(row.get("candidate_retrieval_path"), []),
        )
        records.append(annotation.to_dict())

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(records, handle, ensure_ascii=False, indent=2)
    return output_path


def load_annotations(path: str | Path) -> dict[str, EvidenceAnnotation]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    items = [EvidenceAnnotation(**item) for item in raw]
    by_index = {item.index: item for item in items if item.index}
    if by_index:
        return by_index
    return {item.question: item for item in items}


def _precision_recall_f1(predicted: set[str], gold: set[str]) -> tuple[float, float, float]:
    if not predicted and not gold:
        return 1.0, 1.0, 1.0
    if not predicted:
        return 0.0, 0.0, 0.0
    if not gold:
        return 0.0, 0.0, 0.0
    overlap = len(predicted.intersection(gold))
    precision = overlap / len(predicted) if predicted else 0.0
    recall = overlap / len(gold) if gold else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return precision, recall, f1


def score_against_annotations(
    results_csv: str | Path,
    annotations_path: str | Path,
    *,
    output_path: str | Path | None = None,
    summary_path: str | Path | None = None,
) -> tuple[pd.DataFrame, dict[str, float]]:
    df = pd.read_csv(results_csv)
    annotations = load_annotations(annotations_path)

    scored_rows: list[dict[str, Any]] = []
    for row in df.to_dict(orient="records"):
        row_key = str(row.get("index", row.get("id", ""))) or str(row.get("question", ""))
        annotation = annotations.get(row_key) or annotations.get(str(row.get("question", "")))
        if annotation is None or annotation.annotation_status.lower() != "done":
            continue

        selected_path = _parse_json_field(row.get("retrieval_path"), [])
        predicted_ids = {
            str(item.get("node_id", "")).strip()
            for item in selected_path
            if str(item.get("node_id", "")).strip()
        }
        gold_ids = {str(item).strip() for item in annotation.gold_evidence_node_ids if str(item).strip()}
        contradiction_ids = {str(item).strip() for item in annotation.contradiction_node_ids if str(item).strip()}
        precision, recall, f1 = _precision_recall_f1(predicted_ids, gold_ids)

        sufficient_sets = [
            {str(item).strip() for item in group if str(item).strip()}
            for group in annotation.sufficient_evidence_sets
        ]
        sufficient_hit = 1.0 if any(group and group.issubset(predicted_ids) for group in sufficient_sets) else 0.0
        support_set_scores = support_set_best_match(predicted_ids, sufficient_sets)
        contradiction_exposure = (
            len(predicted_ids.intersection(contradiction_ids)) / len(predicted_ids)
            if predicted_ids else 0.0
        )

        scored_rows.append(
            {
                **row,
                "evidence_precision": precision,
                "evidence_recall": recall,
                "evidence_f1": f1,
                "evidence_set_coverage": sufficient_hit,
                **support_set_scores,
                "contradiction_exposure_rate": contradiction_exposure,
                "annotation_status": annotation.annotation_status,
            }
        )

    scored_df = pd.DataFrame(scored_rows)
    summary = {
        "rows": float(len(scored_df)),
        "evidence_precision": float(scored_df["evidence_precision"].mean()) if "evidence_precision" in scored_df else 0.0,
        "evidence_recall": float(scored_df["evidence_recall"].mean()) if "evidence_recall" in scored_df else 0.0,
        "evidence_f1": float(scored_df["evidence_f1"].mean()) if "evidence_f1" in scored_df else 0.0,
        "evidence_set_coverage": float(scored_df["evidence_set_coverage"].mean()) if "evidence_set_coverage" in scored_df else 0.0,
        "support_set_best_precision": float(scored_df["support_set_best_precision"].mean()) if "support_set_best_precision" in scored_df else 0.0,
        "support_set_best_recall": float(scored_df["support_set_best_recall"].mean()) if "support_set_best_recall" in scored_df else 0.0,
        "support_set_best_f1": float(scored_df["support_set_best_f1"].mean()) if "support_set_best_f1" in scored_df else 0.0,
        "support_set_best_jaccard": float(scored_df["support_set_best_jaccard"].mean()) if "support_set_best_jaccard" in scored_df else 0.0,
        "support_set_exact_match": float(scored_df["support_set_exact_match"].mean()) if "support_set_exact_match" in scored_df else 0.0,
        "contradiction_exposure_rate": float(scored_df["contradiction_exposure_rate"].mean()) if "contradiction_exposure_rate" in scored_df else 0.0,
    }

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        scored_df.to_csv(output_path, index=False)
    if summary_path is not None:
        summary_path = Path(summary_path)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with summary_path.open("w", encoding="utf-8") as handle:
            json.dump(summary, handle, ensure_ascii=False, indent=2)

    return scored_df, summary
