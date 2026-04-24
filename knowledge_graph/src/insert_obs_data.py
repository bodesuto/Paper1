import os
import sys
import hashlib
import re
from pathlib import Path
from typing import Iterable, Dict, Any

# allow imports from repo root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from neo4j import GraphDatabase
from common.config import EMBEDDING_VECTOR_DIMENSIONS
from common.models import get_embeddings
from common.logger import get_logger
from knowledge_graph.cyphers.crud_cyphers import insert_cypher
from knowledge_graph.cyphers.schema_v2 import (
    SCHEMA_V2_CYPHERS,
    build_semantic_vector_index_cypher,
    build_vector_index_cypher,
)
from reasoning_ontology.src.infer import OntologyInferenceEngine


logger = get_logger(__name__)
OBSERVATION_RE = re.compile(
    r"Observation:\s*(.*?)(?=\n(?:Thought:|Action:|Action Input:|Observation:|Final Answer:)|\Z)",
    re.DOTALL,
)


def _infer_success(payload: Dict[str, Any]) -> bool:
    if isinstance(payload.get("success"), bool):
        return payload["success"]
    review_score = payload.get("review_score")
    if review_score is not None:
        try:
            return float(review_score) > 3.0
        except Exception:
            pass
    status = payload.get("status")
    if isinstance(status, bool):
        return status
    return False


def _coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if isinstance(value, tuple):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def _build_weak_concepts(payload: Dict[str, Any]) -> list[Dict[str, str]]:
    vocab = payload.get("vocab") or {}
    concepts: list[Dict[str, str]] = []

    intent = vocab.get("intent")
    if intent:
        concepts.append(
            {
                "key": f"intent::{intent}",
                "name": str(intent),
                "concept_type": "intent",
                "source": "weak_label",
            }
        )

    for attribute in _coerce_list(vocab.get("attributes")):
        concepts.append(
            {
                "key": f"attribute::{attribute}",
                "name": attribute,
                "concept_type": "attribute",
                "source": "weak_label",
            }
        )

    for entity in _coerce_list(vocab.get("entities")):
        concepts.append(
            {
                "key": f"entity::{entity}",
                "name": entity,
                "concept_type": "entity",
                "source": "weak_label",
            }
        )

    return concepts


def _stable_hash(*parts: str) -> str:
    joined = "||".join(part.strip() for part in parts if part and part.strip())
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()


def _extract_observations(trace: str | None) -> list[str]:
    if not trace:
        return []
    items = []
    for match in OBSERVATION_RE.finditer(trace):
        text = match.group(1).strip()
        if text:
            items.append(text)
    return items


def _coerce_text_items(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, dict):
        items: list[str] = []
        for nested in value.values():
            items.extend(_coerce_text_items(nested))
        return items
    if isinstance(value, (list, tuple)):
        items: list[str] = []
        for nested in value:
            items.extend(_coerce_text_items(nested))
        return items
    text = str(value).strip()
    return [text] if text else []


def _concepts_for_text(text: str, weak_concepts: list[Dict[str, str]]) -> list[Dict[str, str]]:
    lowered = text.lower()
    matched = []
    for concept in weak_concepts:
        name = str(concept.get("name", "")).strip().lower()
        if name and name in lowered:
            matched.append(concept)
    return matched or weak_concepts[:2]


def _dedupe_concepts(concepts: list[Dict[str, Any]]) -> list[Dict[str, str]]:
    deduped: list[Dict[str, str]] = []
    seen: set[str] = set()
    for concept in concepts:
        key = str(concept.get("key", "")).strip()
        if not key or key in seen:
            continue
        deduped.append(
            {
                "key": key,
                "name": str(concept.get("name", key)).strip(),
                "concept_type": str(concept.get("concept_type", "unknown")).strip(),
                "source": str(concept.get("source", "unknown")).strip(),
            }
        )
        seen.add(key)
    return deduped


def _assignment_to_concept(assignment: Dict[str, Any]) -> Dict[str, str]:
    prototype_id = str(assignment.get("prototype_id", "")).strip()
    concept_type = str(assignment.get("concept_type", "unknown")).strip() or "unknown"
    label = str(assignment.get("label", prototype_id)).strip() or prototype_id
    return {
        "key": prototype_id,
        "name": label,
        "concept_type": concept_type,
        "source": "learned_ontology",
    }


def _maybe_build_learned_assignments(
    text: str,
    ontology_engine: OntologyInferenceEngine | None,
    *,
    top_k: int = 5,
) -> tuple[list[Dict[str, Any]], list[Dict[str, str]]]:
    if ontology_engine is None:
        return [], []
    text = text.strip()
    if not text:
        return [], []
    assignments = ontology_engine.infer(text, top_k=top_k)
    concepts = [_assignment_to_concept(item) for item in assignments]
    return assignments, _dedupe_concepts(concepts)


def _build_semantic_memories(
    payload: Dict[str, Any],
    embeddings,
    ontology_engine: OntologyInferenceEngine | None = None,
) -> list[Dict[str, Any]]:
    question = str(payload.get("question", "")).strip()
    weak_concepts = payload.get("weak_concepts", [])
    raw_items: list[tuple[str, str]] = []

    for observation in _extract_observations(payload.get("trace")):
        raw_items.append(("trace_observation", observation))

    for key in ("support_passages", "supporting_facts", "evidence", "context", "semantic_memory"):
        for item in _coerce_text_items(payload.get(key)):
            raw_items.append((key, item))

    deduped: list[tuple[str, str]] = []
    seen: set[str] = set()
    for source, text in raw_items:
        normalized = " ".join(text.split())
        if normalized and normalized not in seen:
            deduped.append((source, normalized))
            seen.add(normalized)

    if not deduped:
        return []

    texts = [text for _, text in deduped]
    try:
        embedded = embeddings.embed_documents(texts)
    except Exception:
        embedded = [embeddings.embed_query(text) for text in texts]

    semantic_memories: list[Dict[str, Any]] = []
    for rank, ((source, text), embedding) in enumerate(zip(deduped, embedded)):
        learned_assignments, learned_concepts = _maybe_build_learned_assignments(
            text,
            ontology_engine,
            top_k=3,
        )
        weak_text_concepts = _concepts_for_text(text, weak_concepts)
        semantic_memories.append(
            {
                "key": f"semantic::{_stable_hash(question, text)}",
                "text": text,
                "source": source,
                "rank": rank,
                "embedding": embedding,
                "concepts": _dedupe_concepts(weak_text_concepts + learned_concepts),
                "weak_concepts": [concept["key"] for concept in weak_text_concepts],
                "learned_concepts": [concept["key"] for concept in learned_concepts],
                "assignments": learned_assignments,
            }
        )
    return semantic_memories


def _build_semantic_links(semantic_memories: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    links: list[Dict[str, Any]] = []
    for left, right in zip(semantic_memories, semantic_memories[1:]):
        links.append(
            {
                "from_key": left["key"],
                "to_key": right["key"],
                "relation": "NEXT_HOP",
                "score": 1.0,
            }
        )

    for idx, left in enumerate(semantic_memories):
        left_concepts = {concept["key"] for concept in left.get("concepts", [])}
        for right in semantic_memories[idx + 1 :]:
            right_concepts = {concept["key"] for concept in right.get("concepts", [])}
            overlap = left_concepts.intersection(right_concepts)
            if overlap:
                links.append(
                    {
                        "from_key": left["key"],
                        "to_key": right["key"],
                        "relation": "SIMILAR_TO",
                        "score": float(len(overlap)),
                    }
                )
    return links


def insert_classified_payloads(
    classified: Iterable[Dict[str, Any]],
):
    """Insert classified payloads into Neo4j, adding embeddings to each payload.

    - `classified`: iterable of payload dicts. Each payload must have an `inputs` key.
    - `uri`, `user`, `password`: Neo4j connection parameters. If omitted, read from
      env vars `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.
    - `database`: Neo4j database name to open sessions against.
    """
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE")

    if not uri:
        raise ValueError("NEO4J URI is required (pass uri or set NEO4J_URI env var)")

    auth = None
    if user and password:
        auth = (user, password)

    embeddings = get_embeddings()
    ontology_engine = None
    try:
        candidate_engine = OntologyInferenceEngine()
        if candidate_engine.ensure_loaded():
            ontology_engine = candidate_engine
            logger.info("Loaded ontology prototypes for graph enrichment.")
    except Exception as exc:
        logger.warning("Ontology enrichment disabled because prototypes could not be loaded: %s", exc)

    driver = GraphDatabase.driver(uri, auth=auth)
    inserted = 0
    index_dimensions: int | None = None
    try:
        # Now insert the payloads
        for payload in classified:
            try:
                inputs = payload.get("question")
                if not inputs:
                    logger.warning("Skipping payload without 'question': %s", payload)
                    continue

                # compute embedding for the input text
                try:
                    emb = embeddings.embed_query(inputs)
                except Exception:
                    # fallback to embed_documents if embed_query not available
                    emb = embeddings.embed_documents([inputs])[0]

                if index_dimensions is None:
                    index_dimensions = len(emb)
                    if EMBEDDING_VECTOR_DIMENSIONS is not None and EMBEDDING_VECTOR_DIMENSIONS != index_dimensions:
                        logger.warning(
                            "EMBEDDING_VECTOR_DIMENSIONS=%d but runtime embedding size is %d. Using runtime value for Neo4j indices.",
                            EMBEDDING_VECTOR_DIMENSIONS,
                            index_dimensions,
                        )
                    with driver.session(database=database) as session:
                        for schema_cypher in SCHEMA_V2_CYPHERS:
                            session.run(schema_cypher)
                        session.run(build_vector_index_cypher(index_dimensions))
                        session.run(build_semantic_vector_index_cypher(index_dimensions))
                    logger.info("Schema v2 ensured and vector index prepared with dimension %d", index_dimensions)

                payload["success"] = _infer_success(payload)
                payload["embedding"] = emb
                payload["graph_version"] = payload.get("graph_version", "v2")
                payload["memory_key"] = payload.get(
                    "memory_key",
                    f"trace::{_stable_hash(str(payload.get('question', '')), str(payload.get('trace', '')), str(payload.get('source', '')), str(payload['success']))}",
                )
                payload.setdefault("review_score", payload.get("review_score"))
                payload.setdefault("vocab", {})
                payload["vocab"].setdefault("attributes", payload["vocab"].get("attributes", []))
                payload["vocab"].setdefault("entities", payload["vocab"].get("entities", []))
                payload["weak_concepts"] = _build_weak_concepts(payload)
                trace_text = "\n\n".join(
                    part
                    for part in [
                        str(payload.get("question", "")).strip(),
                        str(payload.get("trace", "")).strip(),
                        str(payload.get("explanation", "")).strip(),
                        str(payload.get("insights", "")).strip(),
                    ]
                    if part
                )
                ontology_assignments, learned_concepts = _maybe_build_learned_assignments(
                    trace_text,
                    ontology_engine,
                )
                payload["ontology_assignments"] = ontology_assignments
                payload["learned_concepts"] = learned_concepts
                payload["semantic_memories"] = _build_semantic_memories(payload, embeddings, ontology_engine)
                payload["semantic_links"] = _build_semantic_links(payload["semantic_memories"])
                payload.setdefault("rca", {})

                with driver.session(database=database) as session:
                    try:
                        session.run(insert_cypher, payload=payload)
                        inserted += 1
                    except Exception as e:
                        logger.exception("Error while adding query %s. Error: %s", inputs, e)

            except Exception:
                logger.exception("Unexpected error processing payload: %s", payload)

    finally:
        driver.close()

    logger.info("Inserted %d payloads into Neo4j", inserted)
    return inserted
