insert_cypher = """
WITH $payload AS data

MERGE (t:Trace { memory_key: data.memory_key })
ON MATCH SET
    t.memory_key = data.memory_key,
    t.question = data.question,
    t.trace = data.trace,
    t.success = data.success,
    t.memory_type = CASE WHEN data.success THEN "experience" ELSE "insight" END,
    t.memory_family = "observability",
    t.explanation = data.rca.explanation,
    t.root_cause = data.rca.root_cause,
    t.insights = data.rca.insights,
    t.embedding = data.embedding,
    t.intent = data.vocab.intent,
    t.entities = data.vocab.entities,
    t.attributes = data.vocab.attributes,
    t.weak_concepts = [concept IN coalesce(data.weak_concepts, []) | concept.key],
    t.learned_concepts = [concept IN coalesce(data.learned_concepts, []) | concept.key],
    t.ontology_assignments_json = apoc.convert.toJson(coalesce(data.ontology_assignments, [])),
    t.review_score = data.review_score,
    t.graph_version = coalesce(data.graph_version, "v2"),
    t.updated_at = timestamp()

ON CREATE SET
    t.id = randomUUID(),
    t.memory_key = data.memory_key,
    t.question = data.question,
    t.trace = data.trace,
    t.success = data.success,
    t.memory_type = CASE WHEN data.success THEN "experience" ELSE "insight" END,
    t.memory_family = "observability",
    t.explanation = data.rca.explanation,
    t.root_cause = data.rca.root_cause,
    t.insights = data.rca.insights,
    t.embedding = data.embedding,
    t.intent = data.vocab.intent,
    t.entities = data.vocab.entities,
    t.attributes = data.vocab.attributes,
    t.weak_concepts = [concept IN coalesce(data.weak_concepts, []) | concept.key],
    t.learned_concepts = [concept IN coalesce(data.learned_concepts, []) | concept.key],
    t.ontology_assignments_json = apoc.convert.toJson(coalesce(data.ontology_assignments, [])),
    t.review_score = data.review_score,
    t.graph_version = coalesce(data.graph_version, "v2"),
    t.created_at = timestamp()

WITH t, data, (CASE WHEN data.success THEN "Experience" ELSE "Insight" END) AS mainLabel
CALL apoc.create.addLabels(t, [mainLabel, "ObservabilityMemory"]) YIELD node AS run_node

MERGE (q:Question { text: data.question })
ON CREATE SET
    q.id = randomUUID(),
    q.created_at = timestamp()
ON MATCH SET
    q.updated_at = timestamp()

MERGE (q)-[:HAS_TRACE]->(run_node)
MERGE (run_node)-[:ABOUT_QUESTION]->(q)

WITH run_node, q, data
FOREACH (attr_name IN coalesce(data.vocab.attributes, []) |
    MERGE (a:Attribute { name: attr_name })
    MERGE (run_node)-[:HAS_ATTRIBUTE]->(a)
)

FOREACH (concept IN coalesce(data.weak_concepts, []) + coalesce(data.learned_concepts, []) |
    MERGE (c:OntologyConcept { key: concept.key })
    ON CREATE SET
        c.name = concept.name,
        c.concept_type = concept.concept_type,
        c.source = concept.source,
        c.created_at = timestamp()
    ON MATCH SET
        c.name = concept.name,
        c.concept_type = concept.concept_type,
        c.source = concept.source,
        c.updated_at = timestamp()
    MERGE (run_node)-[:HAS_CONCEPT { source: concept.source }]->(c)
)

CALL {
    WITH run_node, q, data
    UNWIND coalesce(data.semantic_memories, []) AS mem
    MERGE (s:SemanticMemory { key: mem.key })
    ON CREATE SET
        s.id = randomUUID(),
        s.text = mem.text,
        s.source = mem.source,
        s.rank = mem.rank,
        s.question = data.question,
        s.embedding = mem.embedding,
        s.weak_concepts = coalesce(mem.weak_concepts, []),
        s.learned_concepts = coalesce(mem.learned_concepts, []),
        s.ontology_assignments_json = apoc.convert.toJson(coalesce(mem.assignments, [])),
        s.created_at = timestamp()
    ON MATCH SET
        s.text = mem.text,
        s.source = mem.source,
        s.rank = mem.rank,
        s.question = data.question,
        s.embedding = coalesce(mem.embedding, s.embedding),
        s.weak_concepts = coalesce(mem.weak_concepts, []),
        s.learned_concepts = coalesce(mem.learned_concepts, []),
        s.ontology_assignments_json = apoc.convert.toJson(coalesce(mem.assignments, [])),
        s.updated_at = timestamp()
    MERGE (q)-[:HAS_SEMANTIC_MEMORY]->(s)
    MERGE (run_node)-[sb:SUPPORTED_BY]->(s)
    SET sb.source = mem.source, sb.rank = mem.rank
    FOREACH (_ IN CASE WHEN NOT data.success THEN [1] ELSE [] END |
        MERGE (run_node)-[:CONFLICTS_WITH]->(s)
    )
    FOREACH (concept IN coalesce(mem.concepts, []) |
        MERGE (c:OntologyConcept { key: concept.key })
        ON CREATE SET
            c.name = concept.name,
            c.concept_type = concept.concept_type,
            c.source = concept.source,
            c.created_at = timestamp()
        ON MATCH SET
            c.name = concept.name,
            c.concept_type = concept.concept_type,
            c.source = concept.source,
            c.updated_at = timestamp()
        MERGE (s)-[:HAS_CONCEPT { source: concept.source }]->(c)
    )
    RETURN count(*) AS semantic_count
}

CALL {
    WITH data
    UNWIND coalesce(data.semantic_links, []) AS link
    MATCH (left:SemanticMemory { key: link.from_key })
    MATCH (right:SemanticMemory { key: link.to_key })
    FOREACH (_ IN CASE WHEN link.relation = "NEXT_HOP" THEN [1] ELSE [] END |
        MERGE (left)-[:NEXT_HOP]->(right)
    )
    FOREACH (_ IN CASE WHEN link.relation = "SIMILAR_TO" THEN [1] ELSE [] END |
        MERGE (left)-[r:SIMILAR_TO]->(right)
        SET r.score = link.score
    )
    RETURN count(*) AS link_count
}

RETURN run_node;
"""

export_query = """
MATCH (t:Trace)
OPTIONAL MATCH (t)-[:HAS_ATTRIBUTE]->(a:Attribute)
OPTIONAL MATCH (t)-[:HAS_CONCEPT]->(c:OntologyConcept)
OPTIONAL MATCH (t)-[:SUPPORTED_BY]->(s:SemanticMemory)
WITH t, collect(DISTINCT a.name) AS attributes, collect(DISTINCT c.key) AS concept_keys, collect(DISTINCT s.text) AS semantic_memories
RETURN {
    memory_key: t.memory_key,
    question: t.question,
    trace: t.trace,
    success: t.success,
    memory_type: t.memory_type,
    memory_family: t.memory_family,
    explanation: t.explanation,
    root_cause: t.root_cause,
    insights: t.insights,
    embedding: t.embedding,
    vocab: {
        intent: t.intent,
        entities: t.entities,
        attributes: attributes
    },
    weak_concepts: concept_keys,
    learned_concepts: coalesce(t.learned_concepts, []),
    ontology_assignments_json: coalesce(t.ontology_assignments_json, "[]"),
    semantic_memories: semantic_memories
} AS payload;
"""

embedding_cypher = """
CREATE VECTOR INDEX trace_embedding_index IF NOT EXISTS
FOR (n:Trace) ON (n.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: "cosine"
  }
};
"""

retrieve_cypher = """
WITH
  $query_embedding AS q_emb,
  $intent AS q_intent,
  $attributes AS q_attr,
  $entities AS q_entities

CALL db.index.vector.queryNodes('trace_embedding_index', 50, q_emb)
YIELD node, score AS embedding_score

WITH node, embedding_score,
     CASE WHEN node.intent = q_intent THEN 1 ELSE 0 END AS intent_score,
     apoc.coll.intersection(coalesce(node.attributes, []), q_attr) AS attr_overlap,
     apoc.coll.intersection(coalesce(node.entities, []), q_entities) AS ent_overlap

OPTIONAL MATCH (node)-[:SUPPORTED_BY]->(s:SemanticMemory)
WITH node,
     labels(node) AS labels,
     embedding_score,
     intent_score,
     attr_overlap,
     ent_overlap,
     collect(DISTINCT s.text)[..3] AS semantic_supports,
     (embedding_score +
      intent_score +
      size(attr_overlap) +
      size(ent_overlap)) AS total_score
ORDER BY total_score DESC
LIMIT 12

RETURN
    node,
    coalesce(node.id, elementId(node)) AS node_id,
    labels,
    embedding_score,
    intent_score,
    attr_overlap,
    ent_overlap,
    semantic_supports,
    total_score;
"""

retrieve_vector_only_cypher = """
WITH $query_embedding AS q_emb

CALL db.index.vector.queryNodes('trace_embedding_index', 50, q_emb)
YIELD node, score AS embedding_score

OPTIONAL MATCH (node)-[:SUPPORTED_BY]->(s:SemanticMemory)
WITH node,
     labels(node) AS labels,
     embedding_score,
     collect(DISTINCT s.text)[..3] AS semantic_supports
ORDER BY embedding_score DESC
LIMIT 12

RETURN
    node,
    coalesce(node.id, elementId(node)) AS node_id,
    labels,
    embedding_score,
    0.0 AS intent_score,
    [] AS attr_overlap,
    [] AS ent_overlap,
    semantic_supports,
    embedding_score AS total_score;
"""
