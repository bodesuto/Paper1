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

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "success": self.success,
            "steps": [step.to_dict() for step in self.steps],
        }


def episode_from_retrieval_log(record: dict[str, Any]) -> TraversalEpisode:
    question = str(record.get("question", ""))
    success = bool(record.get("exact_match") or record.get("exact_match_eval"))
    selected_ids = set(record.get("selected_node_ids", []))
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
                },
            )
        )

    return TraversalEpisode(question=question, steps=steps, success=success)
