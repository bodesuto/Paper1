from __future__ import annotations

from typing import Any

from knowledge_graph.src.retrieval_types import RetrievedMemoryBundle, RetrievedMemoryNode


def encode_policy_state(question: str, node: RetrievedMemoryNode, history: list[str] | None = None) -> dict[str, Any]:
    history = history or []
    return {
        "question": question,
        "node_id": node.node_id,
        "memory_type": node.memory_type,
        "memory_family": node.memory_family,
        "score": node.total_score,
        "embedding_score": node.embedding_score,
        "intent_score": node.intent_score,
        "attribute_overlap": node.attribute_overlap,
        "entity_overlap": node.entity_overlap,
        "weak_concepts": node.weak_concepts,
        "ontology_matches": node.ontology_matches,
        "semantic_supports": node.semantic_supports,
        "support_count": len(node.semantic_supports),
        "history": history,
    }


def encode_bundle_states(bundle: RetrievedMemoryBundle) -> list[dict[str, Any]]:
    return [encode_policy_state(bundle.query.text, node) for node in bundle.nodes]
