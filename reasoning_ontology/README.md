# Reasoning Ontology Module

This module is the first implementation step toward the proposal's learned latent ontology.

Current contents:

- `src/dataset.py`
  - builds ontology training examples from current HIL/RCA classified artifacts
- `src/prototype_learner.py`
  - creates weak-label-seeded concept prototypes using Gemini embeddings

Current status:

- suitable for data preparation and weak prototype bootstrapping
- not yet the full latent ontology learner described in `proposal.md`

Planned next steps:

1. add train/val/test dataset splitting
2. add encoder abstraction
3. replace weak-label-only prototypes with learned latent prototypes
4. write ontology assignments back into Neo4j for retrieval-time use
