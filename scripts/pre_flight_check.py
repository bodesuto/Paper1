"""Pre-Flight Check Script for DualMemoryKG Full Run.

Run this BEFORE any large-scale experiment to verify all system components are
operational. Exits with code 1 on any critical failure so CI/CD pipelines can
gate the full run.

Usage:
    python scripts/pre_flight_check.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from common.env_setup import apply_env

apply_env()

PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    tag = PASS if ok else FAIL
    print(f"  {tag}  {name}" + (f"  →  {detail}" if detail else ""))
    results.append((name, ok, detail))
    return ok


# ===========================================================================
# CHECK 1: Environment Variables
# ===========================================================================
print("\n[1/5] Environment Variables")
try:
    from common.config import (
        GOOGLE_API_KEY,
        NEO4J_URI,
        NEO4J_USER,
        NEO4J_PASSWORD,
        NEO4J_DATABASE,
        GEMINI_MODEL_NAME,
    )
    check("GOOGLE_API_KEY", bool(GOOGLE_API_KEY), f"model={GEMINI_MODEL_NAME}")
    check("NEO4J_URI", bool(NEO4J_URI), NEO4J_URI or "NOT SET")
    check("NEO4J_USER", bool(NEO4J_USER))
    check("NEO4J_PASSWORD", bool(NEO4J_PASSWORD))
except Exception as e:
    check("Config import", False, str(e))

# ===========================================================================
# CHECK 2: Neo4j Connectivity + Data Density
# ===========================================================================
print("\n[2/5] Neo4j Database")
try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session(database=NEO4J_DATABASE) if NEO4J_DATABASE else driver.session() as session:
        # Count total Memory nodes
        total = session.run("MATCH (m:Memory) RETURN count(m) AS cnt").single()["cnt"]
        check("Neo4j connection", True, f"{total} Memory nodes found")

        if total == 0:
            check(
                "Graph data density",
                False,
                "CRITICAL: Graph is EMPTY. Run ingestion script first! "
                "marginal_info_gain will be 0.0 for all nodes.",
            )
        else:
            # Count experience vs insight nodes
            exp_cnt = session.run(
                "MATCH (m:Memory) WHERE m.memory_type='experience' RETURN count(m) AS cnt"
            ).single()["cnt"]
            ins_cnt = session.run(
                "MATCH (m:Memory) WHERE m.memory_type='insight' RETURN count(m) AS cnt"
            ).single()["cnt"]
            check(
                "Graph data density",
                total >= 10,
                f"experiences={exp_cnt}, insights={ins_cnt} (recommend ≥100 for meaningful ablation)",
            )

        # Check vector index
        try:
            idx_result = session.run("SHOW INDEXES").data()
            vector_indexes = [r for r in idx_result if "vector" in str(r.get("type", "")).lower()]
            check("Vector index", len(vector_indexes) > 0, f"{len(vector_indexes)} vector index(es) found")
        except Exception as e:
            check("Vector index", False, str(e))

    driver.close()
except Exception as e:
    check("Neo4j connection", False, str(e))

# ===========================================================================
# CHECK 3: LLM / Gemini API
# ===========================================================================
print("\n[3/5] LLM API (Gemini)")
try:
    from common.models import get_llm
    llm = get_llm()
    response = llm.invoke("Answer with exactly one word: what is 1+1?")
    answer = response.content if hasattr(response, "content") else str(response)
    check("Gemini API call", bool(answer), f"response='{answer[:60]}'")
except Exception as e:
    check("Gemini API call", False, str(e))

# ===========================================================================
# CHECK 4: Embedding Model
# ===========================================================================
print("\n[4/5] Embedding Model")
try:
    from common.models import get_embeddings
    embeddings = get_embeddings()
    vec = embeddings.embed_query("test query for pre-flight check")
    check("Embedding model", len(vec) > 0, f"dim={len(vec)}")
except Exception as e:
    check("Embedding model", False, str(e))

# ===========================================================================
# CHECK 5: Information-Theoretic Enrichment
# ===========================================================================
print("\n[5/5] Information-Theoretic Enrichment (it_enrichment)")
try:
    from knowledge_graph.src.retrieve_heuristic import _enrich_nodes_with_it_features
    from knowledge_graph.src.retrieval_types import RetrievedMemoryNode

    dummy_node = RetrievedMemoryNode(
        node_id="test-001",
        labels=["Memory"],
        question="test",
        memory_type="experience",
        memory_family="observability",
        trace=None,
        insight=None,
        explanation=None,
        total_score=0.75,
        embedding_score=0.75,
        intent_score=0.5,
        attribute_overlap=[],
        entity_overlap=[],
        weak_concepts=["bridge", "entity"],
        learned_concepts=[],
        semantic_supports=[],
        metadata={
            "ontology_assignments": [
                {"prototype_id": "proto::bridge", "score": 0.8},
                {"prototype_id": "proto::compare", "score": 0.3},
            ]
        },
    )
    enriched = _enrich_nodes_with_it_features([dummy_node], query_embedding=[0.1] * 10)
    mg = enriched[0].metadata.get("marginal_info_gain", None)
    cv = enriched[0].metadata.get("concept_assignment_variance", None)
    check(
        "IT enrichment active",
        mg is not None and mg != 0.0,
        f"marginal_info_gain={mg:.4f}, concept_variance={cv:.4f}",
    )
except Exception as e:
    check("IT enrichment active", False, str(e))

# ===========================================================================
# SUMMARY
# ===========================================================================
print("\n" + "=" * 60)
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
print(f"  PRE-FLIGHT RESULT:  {passed} passed  |  {failed} failed")

if failed == 0:
    print(f"\n  {PASS} ALL SYSTEMS OPERATIONAL.  You may proceed with Full Run.\n")
    sys.exit(0)
else:
    print(f"\n  {FAIL} {failed} check(s) FAILED.  Fix issues above before running Full.\n")
    sys.exit(1)
