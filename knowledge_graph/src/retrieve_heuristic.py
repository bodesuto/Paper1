import json
import time
from collections.abc import Iterable
from dataclasses import replace

from common.config import ALLOW_DEFAULT_EXAMPLE_PADDING
from common.logger import get_logger
from common.models import get_embeddings
from classifier.src.classifier import classify_hotpot_vocab
from agents.prompts.hotpot_examples import react_examples
from knowledge_graph.cyphers.crud_cyphers import retrieve_cypher, retrieve_vector_only_cypher
from knowledge_graph.src.retrieval_types import (
    RetrievedMemoryBundle,
    RetrievedMemoryNode,
    RetrievalQuery,
)


logger = get_logger(__name__)


def _coerce_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if isinstance(value, tuple):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def _extract_weak_concepts(node: dict) -> list[str]:
    concepts = _coerce_list(node.get("weak_concepts"))
    if concepts:
        return concepts

    generated: list[str] = []
    intent = node.get("intent")
    if intent:
        generated.append(f"intent::{intent}")
    generated.extend(f"attribute::{value}" for value in _coerce_list(node.get("attributes")))
    generated.extend(f"entity::{value}" for value in _coerce_list(node.get("entities")))
    return generated


def _parse_json_like(value: object, default):
    if value is None:
        return default
    if isinstance(value, (list, dict)):
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


def _record_to_memory_node(record) -> RetrievedMemoryNode:
    node = record["node"]
    ontology_assignments = _parse_json_like(node.get("ontology_assignments_json"), [])
    return RetrievedMemoryNode(
        node_id=record.get("node_id"),
        labels=_coerce_list(record.get("labels")),
        question=node.get("question"),
        memory_type=node.get("memory_type"),
        memory_family=node.get("memory_family"),
        trace=node.get("trace"),
        insight=node.get("insights"),
        explanation=node.get("explanation"),
        total_score=float(record.get("total_score", 0.0)),
        embedding_score=float(record["embedding_score"]) if record.get("embedding_score") is not None else None,
        intent_score=float(record["intent_score"]) if record.get("intent_score") is not None else None,
        attribute_overlap=_coerce_list(record.get("attr_overlap")),
        entity_overlap=_coerce_list(record.get("ent_overlap")),
        weak_concepts=_extract_weak_concepts(node),
        learned_concepts=_coerce_list(node.get("learned_concepts")),
        semantic_supports=_coerce_list(record.get("semantic_supports")),
        metadata={
            "root_cause": node.get("root_cause"),
            "review_score": node.get("review_score"),
            "graph_version": node.get("graph_version"),
            "ontology_assignments": ontology_assignments,
        },
    )


def retrieve_memories_heuristic(query: str, session) -> RetrievedMemoryBundle:
    """
    Retrieve memories using the original symbolic + vector heuristic.

    This function is the explicit baseline retrieval path preserved for ablations.
    """
    embeddings = get_embeddings()
    vocab = classify_hotpot_vocab(query)
    logger.debug("Heuristic query vocab: %s", vocab)

    query_embedding = embeddings.embed_query(query)
    params = {
        "query_embedding": query_embedding,
        "intent": vocab.get("intent"),
        "attributes": vocab.get("attributes", []),
        "entities": vocab.get("entities", []),
    }

    start = time.perf_counter()
    result = session.run(retrieve_cypher, **params)
    records = list(result)
    end = time.perf_counter()
    logger.info("Heuristic Cypher retrieval took: %.4fs", end - start)

    nodes = [_record_to_memory_node(record) for record in records]
    return RetrievedMemoryBundle(
        query=RetrievalQuery(
            text=query,
            intent=vocab.get("intent"),
            attributes=_coerce_list(vocab.get("attributes")),
            entities=_coerce_list(vocab.get("entities")),
            strategy="heuristic",
        ),
        nodes=nodes,
        strategy="heuristic",
        metadata={
            "retrieval_latency_s": end - start,
            "candidate_count": len(nodes),
        },
    )


def retrieve_memories_vector_rag(query: str, session, top_k: int = 6) -> RetrievedMemoryBundle:
    """
    Vector-only baseline over the same memory store.

    This approximates a standard dense RAG baseline by ranking only with embedding
    similarity and ignoring symbolic labels, ontology concepts, and traversal policy.
    """
    embeddings = get_embeddings()
    query_embedding = embeddings.embed_query(query)
    start = time.perf_counter()
    result = session.run(retrieve_vector_only_cypher, query_embedding=query_embedding)
    records = list(result)
    end = time.perf_counter()
    nodes = [_record_to_memory_node(record) for record in records]
    base_bundle = RetrievedMemoryBundle(
        query=RetrievalQuery(
            text=query,
            intent=None,
            attributes=[],
            entities=[],
            strategy="vector_rag",
        ),
        nodes=nodes,
        strategy="vector_rag",
        metadata={
            "retrieval_latency_s": end - start,
            "candidate_count": len(nodes),
        },
    )
    nodes = sorted(
        base_bundle.nodes,
        key=lambda node: float(node.embedding_score or 0.0),
        reverse=True,
    )[:top_k]
    return RetrievedMemoryBundle(
        query=replace(base_bundle.query, strategy="vector_rag"),
        nodes=nodes,
        strategy="vector_rag",
        metadata={
            **base_bundle.metadata,
            "rerank_mode": "embedding_only",
            "use_ontology": False,
            "use_traversal": False,
            "traversal": {
                "strategy": "vector_topk",
                "selected_node_ids": [node.node_id for node in nodes[:3] if node.node_id],
                "selected_path": [
                    {
                        "node_id": node.node_id,
                        "memory_type": node.memory_type,
                        "score": float(node.embedding_score or 0.0),
                        "ontology_matches": [],
                    }
                    for node in nodes[:3]
                ],
                "decisions": [],
            },
        },
    )


def retrieve_memories_graph_rag(query: str, session, top_k: int = 6) -> RetrievedMemoryBundle:
    """
    Lightweight graph-aware baseline.

    Start from the vector-similar candidate set, then re-rank by local graph-like
    connectivity proxies already available in memory nodes:
    - shared weak concepts
    - shared attribute/entity overlap
    - memory-type diversity bonus
    """
    base_bundle = retrieve_memories_vector_rag(query, session=session, top_k=max(top_k * 2, 8))
    if not base_bundle.nodes:
        return RetrievedMemoryBundle(
            query=replace(base_bundle.query, strategy="graph_rag"),
            nodes=[],
            strategy="graph_rag",
            metadata={
                **base_bundle.metadata,
                "rerank_mode": "graph_proxy_empty",
            },
        )

    seeds = sorted(
        base_bundle.nodes,
        key=lambda node: float(node.embedding_score or 0.0),
        reverse=True,
    )[:2]
    seed_concepts = {concept for node in seeds for concept in node.weak_concepts}
    seed_attrs = {attr for node in seeds for attr in node.attribute_overlap}
    seed_entities = {ent for node in seeds for ent in node.entity_overlap}

    rescored_nodes: list[RetrievedMemoryNode] = []
    seen_memory_types = {node.memory_type for node in seeds}
    for node in base_bundle.nodes:
        concept_overlap = len(set(node.weak_concepts).intersection(seed_concepts))
        attr_overlap = len(set(node.attribute_overlap).intersection(seed_attrs))
        entity_overlap = len(set(node.entity_overlap).intersection(seed_entities))
        diversity_bonus = 0.2 if node.memory_type not in seen_memory_types else 0.0
        graph_score = float(node.embedding_score or 0.0) + (0.8 * concept_overlap) + (0.4 * attr_overlap) + (0.4 * entity_overlap) + diversity_bonus
        rescored_nodes.append(
            replace(
                node,
                total_score=graph_score,
                metadata={
                    **node.metadata,
                    "base_total_score": node.total_score,
                    "graph_seed_concept_overlap": concept_overlap,
                    "graph_seed_attr_overlap": attr_overlap,
                    "graph_seed_entity_overlap": entity_overlap,
                    "graph_diversity_bonus": diversity_bonus,
                },
            )
        )

    rescored_nodes.sort(key=lambda node: node.total_score, reverse=True)
    nodes = rescored_nodes[:top_k]
    return RetrievedMemoryBundle(
        query=replace(base_bundle.query, strategy="graph_rag"),
        nodes=nodes,
        strategy="graph_rag",
        metadata={
            **base_bundle.metadata,
            "rerank_mode": "graph_proxy",
            "seed_node_ids": [node.node_id for node in seeds if node.node_id],
            "use_ontology": False,
            "use_traversal": False,
            "traversal": {
                "strategy": "graph_proxy_topk",
                "selected_node_ids": [node.node_id for node in nodes[:3] if node.node_id],
                "selected_path": [
                    {
                        "node_id": node.node_id,
                        "memory_type": node.memory_type,
                        "score": node.total_score,
                        "ontology_matches": [],
                    }
                    for node in nodes[:3]
                ],
                "decisions": [],
            },
        },
    )


def bundle_to_prompt_payload(
    bundle: RetrievedMemoryBundle,
    fallback_examples: Iterable[str] | None = None,
    *,
    allow_fallback_examples: bool | None = None,
) -> dict[str, list[str]]:
    traversal = bundle.metadata.get("traversal", {}) or {}
    selected_ids = set(traversal.get("selected_node_ids", []))
    selected_nodes = [node for node in bundle.nodes if node.node_id in selected_ids] if selected_ids else bundle.nodes[:3]
    if not selected_ids:
        selected_ids = {node.node_id for node in selected_nodes if node.node_id}
    selected_bundle = RetrievedMemoryBundle(
        query=bundle.query,
        nodes=selected_nodes,
        strategy=bundle.strategy,
        metadata=bundle.metadata,
    )
    payload = selected_bundle.to_prompt_payload()
    fallback_list = [str(item) for item in (fallback_examples or react_examples)]
    allow_fallback_examples = ALLOW_DEFAULT_EXAMPLE_PADDING if allow_fallback_examples is None else allow_fallback_examples

    if allow_fallback_examples and len(payload["experiences"]) < 3:
        padding_count = 3 - len(payload["experiences"])
        payload["experiences"].extend(fallback_list[:padding_count])
        logger.info("Padded retrieval payload with %d default examples", padding_count)

    return {
        "experiences": payload["experiences"][:3],
        "insights": payload["insights"][:3],
        "ontology_concepts": sorted(
            {
                concept
                for node in selected_nodes[:3]
                for concept in (node.learned_concepts or node.weak_concepts)
                if concept
            }.union(set(bundle.metadata.get("query_concepts", [])))
        ),
        "selected_path": [
            f"{node.memory_type or 'unknown'}::{node.node_id or 'no-id'}::{node.total_score:.4f}"
            for node in selected_nodes[:3]
        ],
        "selected_node_ids": list(selected_ids),
        "grounding_metadata": [
            f"strategy={bundle.strategy}",
            f"candidate_count={bundle.metadata.get('candidate_count', len(bundle.nodes))}",
            f"rerank_mode={bundle.metadata.get('rerank_mode', 'heuristic')}",
            f"traversal_strategy={traversal.get('strategy', 'none')}",
        ],
        "semantic_supports": [
            support
            for node in selected_nodes[:3]
            for support in node.semantic_supports[:2]
            if support
        ][:6],
    }
