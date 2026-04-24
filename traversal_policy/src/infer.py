from __future__ import annotations

from pathlib import Path

from common.config import TRAVERSAL_POLICY_PATH, TRAVERSAL_TOP_K
from knowledge_graph.src.retrieval_types import RetrievedMemoryBundle
from traversal_policy.src.path_builder import build_selected_path
from traversal_policy.src.policy_model import (
    HeuristicTraversalPolicy,
    TraversalDecision,
    WeightedTraversalPolicy,
)


def infer_traversal(bundle: RetrievedMemoryBundle, top_k: int | None = None) -> dict:
    effective_top_k = top_k or TRAVERSAL_TOP_K
    return infer_traversal_with_mode(bundle, top_k=effective_top_k, mode="auto")


def infer_traversal_with_mode(
    bundle: RetrievedMemoryBundle,
    top_k: int | None = None,
    mode: str = "auto",
) -> dict:
    policy_path = Path(TRAVERSAL_POLICY_PATH)
    effective_top_k = top_k or TRAVERSAL_TOP_K

    if mode == "trained":
        if not policy_path.exists():
            raise FileNotFoundError(f"Traversal policy checkpoint not found at {policy_path}")
        policy = WeightedTraversalPolicy.from_file(policy_path)
        policy.top_k = effective_top_k
        strategy = "weighted_policy"
    elif mode == "heuristic":
        policy = HeuristicTraversalPolicy(top_k=effective_top_k)
        strategy = "heuristic_policy_interface"
    elif policy_path.exists():
        policy = WeightedTraversalPolicy.from_file(policy_path)
        policy.top_k = effective_top_k
        strategy = "weighted_policy"
    else:
        policy = HeuristicTraversalPolicy(top_k=effective_top_k)
        strategy = "heuristic_policy_interface"

    selected_nodes, selection = build_selected_path(bundle, policy=policy)
    decisions = selection.get("decisions", [])
    selected_scores = selection.get("selected_scores", {})
    return {
        "strategy": strategy,
        "selected_node_ids": [node.node_id for node in selected_nodes if node.node_id],
        "selected_path": [
            {
                "node_id": node.node_id,
                "memory_type": node.memory_type,
                "score": selected_scores.get(node.node_id, policy.score_node(node)),
                "ontology_matches": node.ontology_matches,
            }
            for node in selected_nodes
        ],
        "decisions": [
            {
                "node_id": decision.get("node_id") if isinstance(decision, dict) else decision.node_id,
                "action": decision.get("action") if isinstance(decision, dict) else decision.action,
                "score": decision.get("score") if isinstance(decision, dict) else decision.score,
                **(
                    {
                        key: value
                        for key, value in decision.items()
                        if key not in {"node_id", "action", "score"}
                    }
                    if isinstance(decision, dict)
                    else {}
                ),
            }
            for decision in decisions
            if isinstance(decision, dict) or isinstance(decision, TraversalDecision)
        ],
        "selector": {
            "frontier_size": selection.get("frontier_size"),
            "objective": selection.get("objective", {}),
        },
    }
