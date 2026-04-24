from __future__ import annotations

from dataclasses import replace

from common.config import LEARNED_RETRIEVAL_TOP_K, ONTOLOGY_TOP_K
from common.logger import get_logger
from knowledge_graph.src.retrieve_heuristic import retrieve_memories_heuristic
from knowledge_graph.src.retrieval_types import RetrievedMemoryBundle, RetrievedMemoryNode
from reasoning_ontology.src.infer import OntologyInferenceEngine
from traversal_policy.src.infer import infer_traversal_with_mode


logger = get_logger(__name__)


def _assignment_map(assignments: list[dict]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for item in assignments or []:
        prototype_id = str(item.get("prototype_id", "")).strip()
        if not prototype_id:
            continue
        try:
            scores[prototype_id] = max(float(item.get("score", 0.0)), scores.get(prototype_id, float("-inf")))
        except Exception:
            scores[prototype_id] = max(0.0, scores.get(prototype_id, float("-inf")))
    return scores


def _query_type_map(assignments: list[dict]) -> dict[str, list[tuple[str, float]]]:
    typed: dict[str, list[tuple[str, float]]] = {}
    for item in assignments or []:
        prototype_id = str(item.get("prototype_id", "")).strip()
        concept_type = str(item.get("concept_type", "")).strip()
        if not prototype_id or not concept_type:
            continue
        try:
            score = float(item.get("score", 0.0))
        except Exception:
            score = 0.0
        typed.setdefault(concept_type, []).append((prototype_id, score))

    for concept_type, items in typed.items():
        items.sort(key=lambda pair: pair[1], reverse=True)
        typed[concept_type] = items
    return typed


def _review_score_boost(node: RetrievedMemoryNode) -> float:
    raw_score = node.metadata.get("review_score")
    try:
        numeric = float(raw_score)
    except Exception:
        return 0.0
    return max(0.0, min(numeric / 5.0, 1.0))


def _node_learned_concepts(
    node: RetrievedMemoryNode,
    inference_engine: OntologyInferenceEngine,
    assignment_cache: dict[str, list[dict]],
) -> tuple[list[str], dict[str, float]]:
    if node.learned_concepts:
        return list(node.learned_concepts), _assignment_map(node.metadata.get("ontology_assignments", []))

    cache_key = node.node_id or node.prompt_text()
    if not cache_key:
        return list(node.weak_concepts), {}

    if cache_key not in assignment_cache:
        text = node.prompt_text()
        assignment_cache[cache_key] = inference_engine.infer(text, top_k=ONTOLOGY_TOP_K) if text else []

    assignments = assignment_cache[cache_key]
    learned_concepts = [str(item.get("prototype_id", "")).strip() for item in assignments if item.get("prototype_id")]
    return learned_concepts, _assignment_map(assignments)


def _concept_boost(
    node: RetrievedMemoryNode,
    query_assignments: list[dict],
    inference_engine: OntologyInferenceEngine,
    assignment_cache: dict[str, list[dict]],
) -> tuple[float, list[str], dict[str, float]]:
    query_scores = _assignment_map(query_assignments)
    query_type_map = _query_type_map(query_assignments)
    query_concepts = set(query_scores)

    node_learned_concepts, node_scores = _node_learned_concepts(node, inference_engine, assignment_cache)
    learned_overlap = sorted(query_concepts.intersection(node_learned_concepts))
    if learned_overlap:
        overlap_score = 0.0
        for concept in learned_overlap:
            query_score = max(query_scores.get(concept, 0.0), 0.05)
            node_score = max(node_scores.get(concept, 0.0), 0.05)
            overlap_score += (query_score * node_score) ** 0.5

        covered_types = {
            concept.split("::", 1)[0]
            for concept in learned_overlap
            if "::" in concept
        }
        type_coverage_bonus = 0.25 * float(len(covered_types))

        top_type_alignment = 0.0
        for concept_type, ranked in query_type_map.items():
            top_query_concept = ranked[0][0] if ranked else None
            if top_query_concept and top_query_concept in node_scores:
                top_type_alignment += 0.2 * max(node_scores.get(top_query_concept, 0.0), 0.05)

        return overlap_score + type_coverage_bonus + top_type_alignment, learned_overlap, node_scores

    weak_overlap = sorted(set(node.weak_concepts).intersection(query_concepts))
    fallback_score = 0.35 * float(len(weak_overlap))
    if node_scores:
        for concept in weak_overlap:
            fallback_score += 0.1 * max(node_scores.get(concept, 0.0), 0.0)
    return fallback_score, weak_overlap, node_scores


def _rerank_node(
    node: RetrievedMemoryNode,
    query_assignments: list[dict],
    inference_engine: OntologyInferenceEngine,
    assignment_cache: dict[str, list[dict]],
) -> RetrievedMemoryNode:
    concept_score, overlap, node_assignment_map = _concept_boost(
        node,
        query_assignments,
        inference_engine,
        assignment_cache,
    )
    review_score = _review_score_boost(node)
    support_bonus = 0.12 * min(len(node.semantic_supports), 3)
    memory_type_bonus = 0.15 if node.memory_type == "experience" else 0.05
    learned_score = (
        node.total_score
        + (1.25 * concept_score)
        + (0.3 * review_score)
        + memory_type_bonus
        + support_bonus
    )

    node_learned_concepts = node.learned_concepts or sorted(node_assignment_map)
    return replace(
        node,
        total_score=learned_score,
        learned_concepts=node_learned_concepts,
        ontology_matches=overlap,
        metadata={
            **node.metadata,
            "base_total_score": node.total_score,
            "concept_score": concept_score,
            "review_score_boost": review_score,
            "memory_type_bonus": memory_type_bonus,
            "support_bonus": support_bonus,
            "node_assignment_scores": node_assignment_map,
        },
    )


def retrieve_memories_adaptive(
    query: str,
    session,
    *,
    use_ontology: bool,
    use_traversal: bool,
    strategy_name: str,
    traversal_mode: str = "auto",
) -> RetrievedMemoryBundle:
    """
    Unified retrieval adapter for proposal ablations.

    Modes:
    - heuristic: no ontology, no traversal
    - ontology_only: ontology reranking, heuristic top-k selection
    - traversal_only: heuristic candidates, traversal policy selection
    - learned/full: ontology reranking + traversal policy selection
    """
    heuristic_bundle = retrieve_memories_heuristic(query, session=session)
    query_assignments: list[dict] = []
    query_concepts: list[str] = []
    rerank_mode = "heuristic"
    nodes = heuristic_bundle.nodes

    if use_ontology:
        inference_engine = OntologyInferenceEngine(top_k=ONTOLOGY_TOP_K)
        query_assignments = inference_engine.infer(query)
        query_concepts = [str(item.get("prototype_id", "")).strip() for item in query_assignments if item.get("prototype_id")]
        if query_concepts:
            assignment_cache: dict[str, list[dict]] = {}
            nodes = [
                _rerank_node(
                    node,
                    query_assignments,
                    inference_engine,
                    assignment_cache,
                )
                for node in nodes
            ]
            nodes.sort(key=lambda node: node.total_score, reverse=True)
            rerank_mode = "ontology_assignments"
        else:
            logger.warning("No ontology prototypes available; '%s' is falling back to heuristic reranking.", strategy_name)
            rerank_mode = "heuristic_fallback"
    else:
        nodes = sorted(nodes, key=lambda node: node.total_score, reverse=True)

    nodes = nodes[:LEARNED_RETRIEVAL_TOP_K]

    bundle = RetrievedMemoryBundle(
        query=replace(heuristic_bundle.query, strategy=strategy_name),
        nodes=nodes,
        strategy=strategy_name,
        metadata={
            **heuristic_bundle.metadata,
            "query_concepts": query_concepts,
            "query_assignments": query_assignments,
            "rerank_mode": rerank_mode,
            "use_ontology": use_ontology,
            "use_traversal": use_traversal,
        },
    )

    if use_traversal:
        bundle.metadata["traversal"] = infer_traversal_with_mode(
            bundle,
            top_k=min(3, len(bundle.nodes) or 1),
            mode=traversal_mode,
        )
    else:
        bundle.metadata["traversal"] = {
            "strategy": "heuristic_topk",
            "selected_node_ids": [node.node_id for node in bundle.nodes[:3] if node.node_id],
            "selected_path": [
                {
                    "node_id": node.node_id,
                    "memory_type": node.memory_type,
                    "score": node.total_score,
                    "ontology_matches": node.ontology_matches,
                }
                for node in bundle.nodes[:3]
            ],
            "decisions": [],
        }

    return bundle


def retrieve_memories_ontology_only(query: str, session) -> RetrievedMemoryBundle:
    return retrieve_memories_adaptive(
        query,
        session,
        use_ontology=True,
        use_traversal=False,
        strategy_name="ontology_only",
        traversal_mode="heuristic",
    )


def retrieve_memories_traversal_only(query: str, session) -> RetrievedMemoryBundle:
    return retrieve_memories_adaptive(
        query,
        session,
        use_ontology=False,
        use_traversal=True,
        strategy_name="traversal_only",
        traversal_mode="heuristic",
    )


def retrieve_memories_learned(query: str, session) -> RetrievedMemoryBundle:
    return retrieve_memories_adaptive(
        query,
        session,
        use_ontology=True,
        use_traversal=True,
        strategy_name="learned",
        traversal_mode="heuristic",
    )


def retrieve_memories_full(query: str, session) -> RetrievedMemoryBundle:
    return retrieve_memories_adaptive(
        query,
        session,
        use_ontology=True,
        use_traversal=True,
        strategy_name="full",
        traversal_mode="trained",
    )
