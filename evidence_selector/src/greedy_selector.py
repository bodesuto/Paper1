from __future__ import annotations

from typing import Any

from common.config import EVIDENCE_FRONTIER_MULTIPLIER, EVIDENCE_SELECTION_BUDGET
from evidence_selector.src.objective import (
    EvidenceSelectionConfig,
    marginal_gain,
    node_concepts,
    node_support_units,
)
from knowledge_graph.src.retrieval_types import RetrievedMemoryBundle, RetrievedMemoryNode


def greedy_select_evidence(
    bundle: RetrievedMemoryBundle,
    *,
    scored_nodes: list[tuple[RetrievedMemoryNode, float]],
    top_k: int | None = None,
    frontier_multiplier: int = EVIDENCE_FRONTIER_MULTIPLIER,
    config: EvidenceSelectionConfig | None = None,
) -> dict[str, Any]:
    config = config or EvidenceSelectionConfig()
    top_k = top_k or EVIDENCE_SELECTION_BUDGET
    frontier_size = max(top_k, frontier_multiplier * top_k)
    frontier = scored_nodes[:frontier_size]

    selected: list[RetrievedMemoryNode] = []
    selected_scores: dict[str | None, float] = {}
    decisions: list[dict[str, Any]] = []
    selected_concepts: set[str] = set()
    selected_support_units: set[str] = set()
    selected_families: set[str] = set()

    remaining = list(frontier)
    while remaining and len(selected) < top_k:
        best_node = None
        best_gain = float("-inf")
        best_terms: dict[str, float] = {}
        best_base_score = 0.0

        for node, base_score in remaining:
            gain, terms = marginal_gain(
                bundle=bundle,
                node=node,
                selected_nodes=selected,
                selected_concepts=selected_concepts,
                selected_support_units=selected_support_units,
                selected_families=selected_families,
                config=config,
                base_score=base_score,
            )
            if gain > best_gain:
                best_node = node
                best_gain = gain
                best_terms = terms
                best_base_score = base_score

        if best_node is None:
            break
        if best_gain <= 0.0 and selected:
            decisions.append(
                {
                    "node_id": None,
                    "action": "stop",
                    "score": best_gain,
                    "reason": "non_positive_marginal_gain",
                }
            )
            break

        selected.append(best_node)
        selected_scores[best_node.node_id] = best_base_score
        remaining = [(node, score) for node, score in remaining if node is not best_node]
        selected_concepts.update(node_concepts(best_node))
        selected_support_units.update(node_support_units(best_node))
        if best_node.memory_family:
            selected_families.add(best_node.memory_family)
        decisions.append(
            {
                "node_id": best_node.node_id,
                "action": "select",
                "score": best_gain,
                "base_score": best_base_score,
                **best_terms,
            }
        )

    if not decisions or decisions[-1].get("action") != "stop":
        decisions.append({"node_id": None, "action": "stop", "score": 0.0, "reason": "budget_reached"})

    return {
        "selected_nodes": selected,
        "selected_scores": selected_scores,
        "decisions": decisions,
        "frontier_size": len(frontier),
        "objective": {
            "query_concept_weight": config.query_concept_weight,
            "support_weight": config.support_weight,
            "family_bonus": config.family_bonus,
            "redundancy_penalty": config.redundancy_penalty,
            "cost_penalty": config.cost_penalty,
        },
    }
