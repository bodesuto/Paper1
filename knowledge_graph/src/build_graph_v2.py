import os

from neo4j import GraphDatabase

from common.config import EMBEDDING_VECTOR_DIMENSIONS
from common.logger import get_logger
from common.models import get_embeddings
from knowledge_graph.cyphers.schema_v2 import (
    SCHEMA_V2_CYPHERS,
    build_semantic_vector_index_cypher,
    build_vector_index_cypher,
)


logger = get_logger(__name__)


def resolve_embedding_dimensions() -> int:
    if EMBEDDING_VECTOR_DIMENSIONS is not None:
        return EMBEDDING_VECTOR_DIMENSIONS

    embeddings = get_embeddings()
    try:
        vector = embeddings.embed_query("dimension probe")
    except Exception:
        vector = embeddings.embed_documents(["dimension probe"])[0]

    resolved = len(vector)
    logger.info("Resolved embedding vector dimension dynamically: %d", resolved)
    return resolved


def ensure_graph_v2_schema(vector_dimensions: int | None = None) -> None:
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE")

    if not uri:
        raise ValueError("Missing NEO4J_URI")

    auth = (user, password) if user and password else None
    effective_dimensions = vector_dimensions or resolve_embedding_dimensions()
    driver = GraphDatabase.driver(uri, auth=auth)
    try:
        with driver.session(database=database) as session:
            for statement in SCHEMA_V2_CYPHERS:
                session.run(statement)
            session.run(build_vector_index_cypher(effective_dimensions))
            session.run(build_semantic_vector_index_cypher(effective_dimensions))
        logger.info("Graph v2 schema ensured with vector dimension %d", effective_dimensions)
    finally:
        driver.close()
