from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RetrievedMemoryNode:
    node_id: str | None
    labels: list[str]
    question: str | None
    memory_type: str | None
    memory_family: str | None
    trace: str | None
    insight: str | None
    explanation: str | None
    total_score: float
    embedding_score: float | None = None
    intent_score: float | None = None
    attribute_overlap: list[str] = field(default_factory=list)
    entity_overlap: list[str] = field(default_factory=list)
    weak_concepts: list[str] = field(default_factory=list)
    learned_concepts: list[str] = field(default_factory=list)
    ontology_matches: list[str] = field(default_factory=list)
    semantic_supports: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def prompt_text(self) -> str:
        support_text = "\n".join(self.semantic_supports[:2]).strip()
        if self.trace:
            return "\n\n".join(part for part in [self.trace, support_text] if part)
        if self.insight:
            return "\n\n".join(part for part in [self.insight, support_text] if part)
        if self.explanation:
            return "\n\n".join(part for part in [self.explanation, support_text] if part)
        return support_text

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RetrievalQuery:
    text: str
    intent: str | None
    attributes: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    strategy: str = "heuristic"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RetrievedMemoryBundle:
    query: RetrievalQuery
    nodes: list[RetrievedMemoryNode]
    strategy: str = "heuristic"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_prompt_payload(self, max_experiences: int = 3, max_insights: int = 3) -> dict[str, list[str]]:
        experiences: list[str] = []
        insights: list[str] = []

        for node in self.nodes:
            if node.memory_type == "experience" and node.trace:
                experiences.append(node.trace)
            elif node.memory_type == "insight":
                text = node.insight or node.explanation
                if text:
                    insights.append(text)

        return {
            "experiences": experiences[:max_experiences],
            "insights": insights[:max_insights],
        }

    def selected_node_ids(self) -> list[str]:
        traversal = self.metadata.get("traversal", {}) or {}
        selected_ids = traversal.get("selected_node_ids", [])
        if selected_ids:
            return [str(node_id) for node_id in selected_ids if node_id]
        return [node.node_id for node in self.nodes if node.node_id]

    def selected_nodes(self) -> list[RetrievedMemoryNode]:
        selected_ids = self.selected_node_ids()
        if not selected_ids:
            return list(self.nodes)

        node_by_id = {node.node_id: node for node in self.nodes if node.node_id}
        selected = [node_by_id[node_id] for node_id in selected_ids if node_id in node_by_id]
        if selected:
            return selected
        return list(self.nodes)

    def memory_types(self) -> list[str]:
        return [node.memory_type or "unknown" for node in self.nodes]

    def selected_memory_types(self) -> list[str]:
        return [node.memory_type or "unknown" for node in self.selected_nodes()]

    def path_summary(self) -> list[dict[str, Any]]:
        return [
            {
                "node_id": node.node_id,
                "memory_type": node.memory_type,
                "memory_family": node.memory_family,
                "labels": node.labels,
                "total_score": node.total_score,
                "base_total_score": node.metadata.get("base_total_score", node.total_score),
                "embedding_score": node.embedding_score,
                "intent_score": node.intent_score,
                "review_score": node.metadata.get("review_score"),
                "attribute_overlap": node.attribute_overlap,
                "entity_overlap": node.entity_overlap,
                "weak_concepts": node.weak_concepts,
                "learned_concepts": node.learned_concepts,
                "ontology_matches": node.ontology_matches,
                "node_assignment_scores": node.metadata.get("node_assignment_scores", {}),
                "ontology_assignments": node.metadata.get("ontology_assignments", []),
                "semantic_supports": node.semantic_supports,
                "text_preview": (node.prompt_text() or "")[:160],
            }
            for node in self.nodes
        ]

    def selected_path_summary(self) -> list[dict[str, Any]]:
        selected_lookup = set(self.selected_node_ids())
        selected_from_traversal = []
        traversal = self.metadata.get("traversal", {}) or {}
        for item in traversal.get("selected_path", []) or []:
            if not isinstance(item, dict):
                continue
            node_id = item.get("node_id")
            matched_node = next((node for node in self.nodes if node.node_id == node_id), None)
            if matched_node is None:
                continue
            selected_from_traversal.append(
                {
                    **next(
                        path_item
                        for path_item in self.path_summary()
                        if path_item.get("node_id") == node_id
                    ),
                    "selected_score": item.get("score"),
                }
            )

        if selected_from_traversal:
            return selected_from_traversal

        if selected_lookup:
            return [item for item in self.path_summary() if item.get("node_id") in selected_lookup]

        return self.path_summary()[:3]

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query.to_dict(),
            "strategy": self.strategy,
            "nodes": [node.to_dict() for node in self.nodes],
            "metadata": self.metadata,
        }
