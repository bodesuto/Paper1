from common.logger import get_logger
from agents.prompts.hotpot_examples import react_examples
from knowledge_graph.src.retrieve_heuristic import (
    bundle_to_prompt_payload,
    retrieve_memories_graph_rag,
    retrieve_memories_heuristic,
    retrieve_memories_vector_rag,
)
from knowledge_graph.src.retrieve_learned import (
    retrieve_memories_full as retrieve_memories_full_bundle,
    retrieve_memories_learned as retrieve_memories_learned_bundle,
    retrieve_memories_ontology_only as retrieve_memories_ontology_only_bundle,
    retrieve_memories_traversal_only as retrieve_memories_traversal_only_bundle,
)
from knowledge_graph.src.retrieval_types import RetrievedMemoryBundle


logger = get_logger(__name__)


def retrieve_memory_bundle(query: str, session, strategy: str = "heuristic") -> RetrievedMemoryBundle:
    """
    Retrieve a structured bundle of memories for downstream analysis/evaluation.

    For now only the heuristic strategy is implemented. This wrapper exists so the
    learned retrieval/traversal path can be added without changing agent runners.
    """
    if strategy == "ontology_only":
        return retrieve_memories_ontology_only_bundle(query, session=session)
    if strategy == "traversal_only":
        return retrieve_memories_traversal_only_bundle(query, session=session)
    if strategy == "vector_rag":
        return retrieve_memories_vector_rag(query, session=session)
    if strategy == "graph_rag":
        return retrieve_memories_graph_rag(query, session=session)
    if strategy == "learned":
        return retrieve_memories_learned_bundle(query, session=session)
    if strategy == "full":
        return retrieve_memories_full_bundle(query, session=session)
    if strategy != "heuristic":
        logger.warning("Retrieval strategy '%s' is not implemented yet. Falling back to heuristic.", strategy)
    return retrieve_memories_heuristic(query, session=session)


def retrieve_memories(query, session, strategy: str = "heuristic"):
    """
    Backward-compatible prompt payload for existing ReAct/Reflexion code paths.

    Returns:
        dict: {"experiences": [...], "insights": [...]}
    """
    bundle = retrieve_memory_bundle(query, session=session, strategy=strategy)
    return bundle_to_prompt_payload(bundle, fallback_examples=react_examples)


def retrieve_memories_learned(query: str, session) -> RetrievedMemoryBundle:
    """
    Placeholder for the future learned ontology/traversal retrieval path.
    """
    return retrieve_memories_learned_bundle(query, session=session)


__all__ = [
    "retrieve_memories",
    "retrieve_memory_bundle",
    "retrieve_memories_learned",
]
