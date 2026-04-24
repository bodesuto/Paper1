import json
import os
from pathlib import Path

from neo4j import GraphDatabase

from common.logger import get_logger
from knowledge_graph.cyphers.crud_cyphers import export_query


logger = get_logger(__name__)


def export_graph_payloads(output_path: str | Path) -> Path:
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE")

    if not uri:
        raise ValueError("Missing NEO4J_URI")

    auth = (user, password) if user and password else None
    driver = GraphDatabase.driver(uri, auth=auth)
    try:
        with driver.session(database=database) as session:
            payloads = [record["payload"] for record in session.run(export_query)]
    finally:
        driver.close()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payloads, handle, ensure_ascii=False, indent=2)

    logger.info("Exported %d graph payloads -> %s", len(payloads), output_path)
    return output_path
