# Knowledge Graph Utils Module (Neo4j CRUD + Memory Retrieval)

This module stores evaluated traces in **Neo4j** and retrieves the most relevant past traces (“memories”) to augment the agent prompt.

---

## Files

```

knowledge_graph/
├── cyphers/
│   └── crud_cyphers.py        # Cypher queries (insert / export / index / retrieve)
└── src/
    ├── insert_obs_data.py     # Insert classified payloads + embeddings into Neo4j
    └── retrieve_data.py       # Retrieve top-k traces for a new query

```

## Insert traces (`src/insert_obs_data.py`)

### `insert_classified_payloads(classified)`
Takes an iterable of classified payloads (already containing `question`, `trace`, `rca`, `vocab`, etc.), computes an embedding for the question, ensures the vector index exists, and inserts each payload into Neo4j.

**Required env vars**
- `NEO4J_URI`
- `NEO4J_USER` / `NEO4J_PASSWORD` (if auth enabled)
- `NEO4J_DATABASE` (optional)

**Usage**
```python
from knowledge_graph.src.insert_obs_data import insert_classified_payloads

inserted = insert_classified_payloads(classified_payloads)
print("Inserted:", inserted)
```

---

## Retrieve memories (`src/retrieve_data.py`)

### `retrieve_memories(query, session)`

Given a new question:

1. Classifies the query (`intent`, `attributes`, `entities`)
2. Embeds the query
3. Runs `retrieve_cypher` in Neo4j
4. Returns up to **3** retrieved traces
5. If fewer than 3 are found, pads with default `react_examples`

**Usage**

```python
from neo4j import GraphDatabase
from knowledge_graph.src.retrieve_data import retrieve_memories

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
with driver.session(database=NEO4J_DATABASE) as session:
    memories = retrieve_memories("Your question here", session)
```
