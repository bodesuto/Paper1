from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TraversalStepRecord:
    question: str
    node_id: str | None
    memory_type: str | None
    score: float
    step_index: int
    selected: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TraversalEpisode:
    question: str
    steps: list[TraversalStepRecord]
    success: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "success": self.success,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": self.metadata,
        }


def episode_from_retrieval_log(record: dict[str, Any]) -> TraversalEpisode:
    question = str(record.get("question", ""))
    success = bool(record.get("exact_match") or record.get("exact_match_eval"))
    selected_path = record.get("selected_retrieval_path", []) or []
    selected_ids = set(record.get("selected_node_ids", []))
    if not selected_ids:
        selected_ids = {
            item.get("node_id")
            for item in selected_path
            if isinstance(item, dict) and item.get("node_id") is not None
        }
    selected_scores = {
        item.get("node_id"): float(item.get("selected_score", item.get("total_score", item.get("score", 0.0))))
        for item in selected_path
        if isinstance(item, dict) and item.get("node_id") is not None
    }

    exact_match_eval = float(record.get("exact_match_eval", 1.0 if success else 0.0) or 0.0)
    path_grounding_precision = float(record.get("path_grounding_precision", 0.0) or 0.0)
    evidence_sufficiency_rate = float(record.get("evidence_sufficiency_rate", 0.0) or 0.0)
    unsupported_reasoning_score = float(record.get("unsupported_reasoning_score", 0.0) or 0.0)
    contradiction_exposure_rate = float(record.get("contradiction_exposure_rate", 0.0) or 0.0)
    supervision_weight = max(
        0.0,
        min(
            1.0,
            (0.50 * exact_match_eval)
            + (0.25 * path_grounding_precision)
            + (0.25 * evidence_sufficiency_rate),
        ),
    )
    steps: list[TraversalStepRecord] = []

    for idx, item in enumerate(record.get("retrieval_path", [])):
        item = item or {}
        node_id = item.get("node_id")
        steps.append(
            TraversalStepRecord(
                question=question,
                node_id=node_id,
                memory_type=item.get("memory_type"),
                score=float(item.get("total_score", item.get("score", 0.0))),
                step_index=idx,
                selected=node_id in selected_ids if node_id is not None else False,
                metadata={
                    "labels": item.get("labels", []),
                    "memory_family": item.get("memory_family"),
                    "attribute_overlap": item.get("attribute_overlap", []),
                    "entity_overlap": item.get("entity_overlap", []),
                    "weak_concepts": item.get("weak_concepts", []),
                    "ontology_matches": item.get("ontology_matches", []),
                    "semantic_supports": item.get("semantic_supports", []),
                    "base_total_score": item.get("base_total_score", item.get("total_score", 0.0)),
                    "embedding_score": item.get("embedding_score", 0.0),
                    "intent_score": item.get("intent_score", 0.0),
                    "review_score": item.get("review_score", 0.0),
                    "candidate_rank": idx,
                    "selected_score": selected_scores.get(node_id, 0.0),
                    "selection_source": "selected_path" if node_id in selected_ids else "candidate_only",
                },
            )
        )

    return TraversalEpisode(
        question=question,
        steps=steps,
        success=success,
        metadata={
            "exact_match_eval": exact_match_eval,
            "path_grounding_precision": path_grounding_precision,
            "evidence_sufficiency_rate": evidence_sufficiency_rate,
            "unsupported_reasoning_score": unsupported_reasoning_score,
            "contradiction_exposure_rate": contradiction_exposure_rate,
            "supervision_weight": supervision_weight,
        },
    )
