SCHEMA_V2_CYPHERS = [
    """
    DROP CONSTRAINT trace_question_unique IF EXISTS
    """,
    """
    CREATE CONSTRAINT trace_memory_key_unique IF NOT EXISTS
    FOR (t:Trace)
    REQUIRE t.memory_key IS UNIQUE
    """,
    """
    CREATE CONSTRAINT question_text_unique IF NOT EXISTS
    FOR (q:Question)
    REQUIRE q.text IS UNIQUE
    """,
    """
    CREATE CONSTRAINT ontology_concept_key_unique IF NOT EXISTS
    FOR (c:OntologyConcept)
    REQUIRE c.key IS UNIQUE
    """,
    """
    CREATE CONSTRAINT semantic_memory_key_unique IF NOT EXISTS
    FOR (s:SemanticMemory)
    REQUIRE s.key IS UNIQUE
    """,
    """
    CREATE CONSTRAINT attribute_name_unique IF NOT EXISTS
    FOR (a:Attribute)
    REQUIRE a.name IS UNIQUE
    """,
]


def build_vector_index_cypher(dimensions: int = 1536) -> str:
    return f"""
    CREATE VECTOR INDEX trace_embedding_index IF NOT EXISTS
    FOR (n:Trace) ON (n.embedding)
    OPTIONS {{
      indexConfig: {{
        `vector.dimensions`: {dimensions},
        `vector.similarity_function`: "cosine"
      }}
    }};
    """


def build_semantic_vector_index_cypher(dimensions: int = 1536) -> str:
    return f"""
    CREATE VECTOR INDEX semantic_memory_embedding_index IF NOT EXISTS
    FOR (n:SemanticMemory) ON (n.embedding)
    OPTIONS {{
      indexConfig: {{
        `vector.dimensions`: {dimensions},
        `vector.similarity_function`: "cosine"
      }}
    }};
    """
