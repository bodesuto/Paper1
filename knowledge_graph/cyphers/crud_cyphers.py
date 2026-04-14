insert_cypher = """
WITH $payload AS data

MERGE (t:Trace { question: data.question })
ON MATCH SET
    t.trace        = data.trace,
    t.success      = data.success,
    t.memory_type  = CASE WHEN data.success THEN "experience" ELSE "insight" END,
    t.explanation  = data.rca.explanation,
    t.root_cause   = data.rca.root_cause,
    t.insights     = data.rca.insights,
    t.embedding    = data.embedding,
    t.intent       = data.vocab.intent,
    t.entities     = data.vocab.entities,
    t.attributes   = data.vocab.attributes,
    t.review_score = data.review_score,
    t.updated_at   = timestamp()

ON CREATE SET
    t.id           = randomUUID(),
    t.trace        = data.trace,
    t.success      = data.success,
    t.memory_type  = CASE WHEN data.success THEN "experience" ELSE "insight" END,
    t.explanation  = data.rca.explanation,
    t.root_cause   = data.rca.root_cause,
    t.insights     = data.rca.insights,
    t.embedding    = data.embedding,
    t.intent       = data.vocab.intent,
    t.entities     = data.vocab.entities,
    t.attributes   = data.vocab.attributes,
    t.review_score = data.review_score,
    t.created_at   = timestamp()

WITH t, data,
     (CASE WHEN data.success THEN "Experience" ELSE "Insight" END) AS mainLabel
CALL apoc.create.addLabels(t, [mainLabel]) YIELD node as run_node

WITH run_node, data
UNWIND data.vocab.attributes AS attr_name
MERGE (a:Attribute { name: attr_name })
MERGE (run_node)-[:HAS_ATTRIBUTE]->(a)

RETURN run_node;
"""
export_query = """
MATCH (t:Trace)
OPTIONAL MATCH (t)-[:HAS_ATTRIBUTE]->(a:Attribute)
WITH t, collect(a.name) AS attributes
RETURN {
    question: t.question,
    trace: t.trace,
    success: t.success,
    memory_type: t.memory_type,
    explanation: t.explanation,
    root_cause: t.root_cause,
    insights: t.insights,
    embedding: t.embedding,
    vocab: {
        intent: t.intent,
        entities: t.entities,
        attributes: attributes
    }
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

// Get top-$k by pure vector similarity first
CALL db.index.vector.queryNodes('trace_embedding_index', 50, q_emb)
YIELD node, score AS embedding_score

// Compute symbolic matches
WITH node, embedding_score,
     CASE WHEN node.intent = q_intent THEN 1 ELSE 0 END AS intent_score,
     apoc.coll.intersection(node.attributes, q_attr) AS attr_overlap,
     apoc.coll.intersection(node.entities,  q_entities) AS ent_overlap

// Equal-weight combined score
WITH node,
     labels(node) AS labels,
     (embedding_score +
      intent_score +
      size(attr_overlap) +
      size(ent_overlap)) AS total_score
ORDER BY total_score DESC
LIMIT 12

RETURN node, labels, total_score;
    """
