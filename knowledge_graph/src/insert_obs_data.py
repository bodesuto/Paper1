import os
import sys
from pathlib import Path
from typing import Iterable, Dict, Any, Optional

# allow imports from repo root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from neo4j import GraphDatabase
from common.models import get_embeddings
from common.logger import get_logger
from knowledge_graph.cyphers.crud_cyphers import insert_cypher, embedding_cypher


logger = get_logger(__name__)


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

    driver = GraphDatabase.driver(uri, auth=auth)
    inserted = 0
    try:
        # First, create the embedding vector index if it doesn't exist
        with driver.session(database=database) as session:
            try:
                session.run(embedding_cypher)
                logger.info("Vector embedding index created or already exists")
            except Exception as e:
                logger.warning("Embedding index creation failed (may already exist): %s", e)
        
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

                payload["success"] = _infer_success(payload)
                payload["embedding"] = emb
                payload.setdefault("review_score", payload.get("review_score"))
                payload.setdefault("vocab", {})
                payload["vocab"].setdefault("attributes", payload["vocab"].get("attributes", []))
                payload["vocab"].setdefault("entities", payload["vocab"].get("entities", []))

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
