from __future__ import annotations

from knowledge_graph.src.retrieval_types import RetrievedMemoryBundle, RetrievedMemoryNode
from traversal_policy.src.policy_model import HeuristicTraversalPolicy
from evidence_selector.src.greedy_selector import greedy_select_evidence


def build_selected_path(
    bundle: RetrievedMemoryBundle,
    policy: HeuristicTraversalPolicy | None = None,
) -> tuple[list[RetrievedMemoryNode], dict]:
    policy = policy or HeuristicTraversalPolicy()
    scored_nodes = policy.rank_nodes(bundle)
    selection = greedy_select_evidence(bundle, scored_nodes=scored_nodes, top_k=policy.top_k)
    return selection["selected_nodes"], selection
