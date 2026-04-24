# Proposal-to-Code Implementation Map

## Goal

This document maps the research proposal in `proposal.md` to concrete code work inside the current `DualMemoryKG` repository. It is written as an implementation backlog for turning the current heuristic dual-memory system into the proposed Q1-grade research framework.

The proposal introduces two main novelties:

1. a learned latent reasoning ontology
2. a learned traversal policy over the dual-memory graph

The current repository already provides:

- LLM runtime and prompting
- ReAct and Reflexion agents
- observability export and diagnostics pipeline
- Neo4j-based dual-memory storage
- evaluation scripts

So the implementation plan should preserve the existing pipeline and replace only the parts that are currently heuristic.

## 1. Current Execution Map

The current primary path of the repository is:

1. Export traces from the observability backend
   - `scripts/run_export.py`
   - `log_transformation/src/log_extractor.py`
2. Convert raw runs into ReAct-style traces
   - `scripts/run_format_trace.py`
   - `log_transformation/src/log_formatter.py`
3. Diagnose traces
   - `scripts/run_rca.py`
   - `diagnostics/rca/src/rca.py`
   - `scripts/run_kbv.py`
   - `diagnostics/kbv/src/kbv.py`
4. Human review and trace classification
   - `scripts/run_hil_streamlit.py`
   - `diagnostics/hil/src/app.py`
   - `diagnostics/hil/src/hil.py`
   - `scripts/run_classify.py`
   - `classifier/src/classifier.py`
5. Insert memories into Neo4j
   - `scripts/run_insert_obs.py`
   - `knowledge_graph/src/insert_obs_data.py`
   - `knowledge_graph/cyphers/crud_cyphers.py`
6. Retrieve memories for agent runs
   - `knowledge_graph/src/retrieve_data.py`
   - `classifier/src/classifier.py`
7. Run baseline and dual-memory evaluation
   - `scripts/run_react_agent.py`
   - `scripts/run_reflexion_agent.py`
   - `agents/src/react.py`
   - `agents/src/reflexion.py`
   - `eval/test/react_test.py`
   - `eval/test/reflexion_test.py`

## 2. Proposal Component to Repo Component

## A. LLM Execution Layer

### Proposal role

Keep the LLM fixed. Treat it as the downstream executor, not the scientific novelty.

### Current files

- `common/models.py`
- `common/config.py`
- `agents/src/react.py`
- `agents/src/reflexion.py`

### Current status

- Already usable with Gemini
- Prompting and agent control exist
- Good enough as fixed execution backbone

### Required code work

- Do not redesign this area early
- Only add minimal hooks so the agent can consume richer retrieved memory payloads

### Concrete implementation items

1. Extend the memory payload format accepted by `agents/src/react.py`
   - currently `format_examples()` only supports simple `experiences` and `insights`
   - new format should also support:
     - ontology concepts
     - selected path
     - grounding metadata
2. Add structured trace logging in:
   - `agents/src/react.py`
   - `agents/src/reflexion.py`
   so each run records:
   - visited memory nodes
   - selected memory type
   - traversal decisions
   - final path summary

### Suggested new files

- `agents/src/memory_prompt_formatter.py`

## B. Heuristic Query Classification

### Proposal role

This is the part that the proposal wants to replace with a learned latent ontology.

### Current files

- `classifier/src/classifier.py`
- `classifier/prompts/classifier_prompts.py`
- `knowledge_graph/src/retrieve_data.py`

### Current status

The current retrieval path depends on:

- `classify_hotpot_vocab(question)`
- LLM-generated symbolic fields:
  - `intent`
  - `attributes`
  - `entities`

These fields are then used in `retrieve_data.py` and Neo4j Cypher ranking.

### Why this is the first scientific bottleneck

This is exactly the handcrafted schema criticized in the proposal.

### Required code work

Replace or augment symbolic classification with a trainable ontology module.

### Concrete implementation items

1. Freeze the current classifier as baseline
   - keep `classifier/src/classifier.py` unchanged for baseline experiments
2. Add a learned ontology package
   - suggested new folder: `reasoning_ontology/`
3. Build training data from existing artifacts
   - source candidates:
     - HIL-reviewed successful traces
     - RCA outputs
     - question-trace pairs already exported
4. Implement an ontology encoder
   - encode:
     - question
     - trace
     - memory node text
5. Implement prototype induction
   - clustering or prototype learning
6. Output ontology assignments per example
   - for example:
     - `prototype_ids`
     - `prototype_scores`
     - optional `prototype_labels`

### Suggested new files

- `reasoning_ontology/src/dataset.py`
- `reasoning_ontology/src/encoders.py`
- `reasoning_ontology/src/prototype_learner.py`
- `reasoning_ontology/src/infer.py`
- `reasoning_ontology/src/export_assignments.py`
- `reasoning_ontology/README.md`

### Existing files to modify

- `scripts/run_classify.py`
  - add an optional learned-ontology path
- `knowledge_graph/src/insert_obs_data.py`
  - insert ontology outputs into Neo4j
- `knowledge_graph/src/retrieve_data.py`
  - query with ontology representations instead of only symbolic labels

## C. Dual-Memory Graph Schema

### Proposal role

The graph must represent:

- semantic memory
- observability memory
- latent ontology nodes
- richer edges for support, conflict, membership, and traversal

### Current files

- `knowledge_graph/cyphers/crud_cyphers.py`
- `knowledge_graph/src/insert_obs_data.py`
- `knowledge_graph/src/retrieve_data.py`

### Current status

The current schema mainly stores:

- `Trace`
- dynamic labels `Experience` or `Insight`
- `Attribute`
- embedded text vector
- simple symbolic fields on the trace node

This is enough for the baseline, but not enough for the proposed paper.

### Required code work

Upgrade the graph from a flat retrieval index into a research-grade heterogeneous memory graph.

### Concrete implementation items

1. Add explicit node families
   - `SemanticMemory`
   - `ObservabilityMemory`
   - `OntologyConcept`
   - optionally `Question`
2. Split current `Trace` responsibilities
   - successful traces should map to observability/experience memory
   - failure analyses should map to observability/insight memory
3. Add edge types
   - `HAS_CONCEPT`
   - `SUPPORTED_BY`
   - `CONFLICTS_WITH`
   - `SIMILAR_TO`
   - `NEXT_HOP`
4. Store traversal-ready features
   - memory type
   - concept memberships
   - success/failure label
   - review score
   - source provenance

### Suggested new files

- `knowledge_graph/cyphers/schema_v2.py`
- `knowledge_graph/src/build_graph_v2.py`
- `knowledge_graph/src/export_graph_training_data.py`

### Existing files to modify

- `knowledge_graph/cyphers/crud_cyphers.py`
- `knowledge_graph/src/insert_obs_data.py`
- `scripts/run_insert_obs.py`

## D. Heuristic Retrieval

### Proposal role

This becomes the baseline retrieval policy.

### Current files

- `knowledge_graph/src/retrieve_data.py`
- `knowledge_graph/cyphers/crud_cyphers.py`

### Current status

The current retrieval score is:

- embedding similarity
- intent equality
- attribute overlap
- entity overlap

That is the exact heuristic mechanism the proposal aims to surpass.

### Required code work

Preserve this path as the baseline, then add a learned retrieval and traversal path beside it.

### Concrete implementation items

1. Keep current `retrieve_memories()` as:
   - `retrieve_memories_heuristic()`
2. Add a new learned retrieval path:
   - `retrieve_memories_learned()`
3. Return structured retrieval output instead of prompt text only
   - node ids
   - scores
   - memory type
   - concept assignments
   - chosen path

### Suggested new files

- `knowledge_graph/src/retrieve_heuristic.py`
- `knowledge_graph/src/retrieve_learned.py`
- `knowledge_graph/src/retrieval_types.py`

### Existing files to modify

- `knowledge_graph/src/retrieve_data.py`
- `eval/test/react_test.py`
- `eval/test/reflexion_test.py`

## E. Traversal Policy Learner

### Proposal role

This is the second core novelty.

### Current status

There is no traversal policy module yet. The current system does one-shot retrieval from Neo4j and directly injects memories into the prompt.

### Required code work

Create a trainable traversal layer between retrieval and final prompt construction.

### Concrete implementation items

1. Create a traversal state representation
   - query embedding
   - current node embedding
   - memory type
   - ontology concept vector
   - history summary
2. Define traversal actions
   - move to next node
   - switch memory family
   - stop
3. Build supervision from historical traces
   - successful HIL-approved runs
   - RCA/KBV filtered good trajectories
4. Implement imitation-learning first
   - avoid pure RL in v1
5. Add inference-time path selection
   - output chosen node sequence and step scores

### Suggested new files

- `traversal_policy/src/dataset.py`
- `traversal_policy/src/state_encoder.py`
- `traversal_policy/src/policy_model.py`
- `traversal_policy/src/train.py`
- `traversal_policy/src/infer.py`
- `traversal_policy/src/path_builder.py`
- `traversal_policy/README.md`

### Existing files to modify

- `knowledge_graph/src/retrieve_data.py`
- `agents/src/react.py`
- `agents/src/reflexion.py`
- `scripts/run_react_agent.py`
- `scripts/run_reflexion_agent.py`

## F. Training Data Generation

### Proposal role

The learned ontology and traversal policy both need supervision.

### Current files

- `scripts/run_export.py`
- `scripts/run_format_trace.py`
- `scripts/run_rca.py`
- `scripts/run_kbv.py`
- `scripts/run_classify.py`
- `diagnostics/rca/src/rca.py`
- `diagnostics/kbv/src/kbv.py`
- `classifier/src/classifier.py`

### Current status

The repository already generates rich intermediate artifacts:

- exported traces
- RCA labels
- KBV scoring
- HIL review scores
- symbolic classification

These are exactly what should seed the new learning modules.

### Required code work

Add dataset builders that convert current artifacts into trainable supervision.

### Concrete implementation items

1. Build ontology training records from:
   - `question`
   - `trace`
   - `success`
   - `rca`
   - `review_score`
   - current symbolic vocab as weak labels
2. Build traversal supervision from:
   - retrieved candidate nodes
   - chosen successful path
   - final success label
3. Add artifact versioning
   - train/val/test splits for ontology learning
   - train/val/test splits for policy learning

### Suggested new files

- `data_pipeline/build_ontology_dataset.py`
- `data_pipeline/build_policy_dataset.py`
- `data_pipeline/split_datasets.py`
- `data_pipeline/README.md`

### Existing files to modify

- `scripts/run_classify.py`
- `scripts/run_insert_obs.py`

## G. Evaluation Layer

### Proposal role

The paper needs grounding-centered evaluation, not just answer accuracy.

### Current files

- `eval/test/react_test.py`
- `eval/test/reflexion_test.py`
- `eval/test/matrics.py`
- `eval/test/utils.py`
- `diagnostics/kbv/src/kbv.py`

### Current status

The current evaluation already measures:

- exact match
- answer relevancy
- faithfulness
- context precision
- inconsistency metrics
- latency and token placeholders

This is a good base, but it does not yet measure:

- unsupported reasoning relative to selected path
- path quality
- memory family selection quality
- transfer under memory perturbation

### Required code work

Extend the evaluation suite to directly test the proposal claims.

### Concrete implementation items

1. Add path-aware metrics
   - Unsupported Reasoning Rate
   - Path Grounding Precision
   - Memory Selection Accuracy
   - Evidence Sufficiency Rate
2. Store retrieval traces during evaluation
   - selected node ids
   - traversal path
   - final prompt memory payload
3. Add robustness benchmarks
   - noisy memory injection
   - missing memory nodes
   - contradictory insight injection
   - low-budget traversal
4. Add transfer evaluation
   - in-domain vs out-of-domain results

### Suggested new files

- `eval/test/grounding_metrics.py`
- `eval/test/path_metrics.py`
- `eval/test/stress_tests.py`
- `eval/test/transfer_eval.py`
- `eval/README_q1.md`

### Existing files to modify

- `eval/test/react_test.py`
- `eval/test/reflexion_test.py`
- `eval/test/matrics.py`

## H. Experiment Runners and Reproducibility

### Proposal role

The paper will need clean experiment entry points and reproducible ablations.

### Current files

- `scripts/run_react_agent.py`
- `scripts/run_reflexion_agent.py`
- `scripts/run_react_smoke.py`
- `scripts/run_reflexion_smoke.py`
- `scripts/run_prepare_mini_data.py`

### Required code work

Turn the current scripts into experiment drivers with explicit modes.

### Concrete implementation items

1. Add experiment mode flags
   - baseline
   - heuristic dual memory
   - ontology-only
   - traversal-only
   - ontology-plus-traversal
2. Save per-run config
   - model name
   - retrieval mode
   - graph version
   - ontology checkpoint
   - policy checkpoint
3. Save structured outputs to experiment folders
   - metrics csv
   - run json
   - selected path json

### Suggested new files

- `scripts/run_experiment.py`
- `scripts/run_ablation_suite.py`
- `scripts/run_stress_suite.py`

### Existing files to modify

- `scripts/run_react_agent.py`
- `scripts/run_reflexion_agent.py`
- `README.md`
- `scripts/README.md`

## 3. Recommended New Top-Level Structure

To keep the repo organized, add these folders:

```text
reasoning_ontology/
traversal_policy/
data_pipeline/
experiments/
```

Suggested purpose:

- `reasoning_ontology/`: learned latent concept module
- `traversal_policy/`: graph traversal learner
- `data_pipeline/`: convert repo artifacts into training/eval data
- `experiments/`: run configs, outputs, ablation manifests

## 4. Priority Order

## Phase 0. Freeze the Baseline

Do first:

1. keep current heuristic pipeline runnable
2. rename and isolate heuristic retrieval and symbolic classifier as baselines
3. ensure evaluation scripts can compare multiple retrieval modes

Main files:

- `classifier/src/classifier.py`
- `knowledge_graph/src/retrieve_data.py`
- `eval/test/react_test.py`
- `eval/test/reflexion_test.py`

## Phase 1. Data and Graph Upgrade

Do next:

1. upgrade graph schema
2. export trainable datasets for ontology and policy
3. store richer memory metadata

Main files:

- `knowledge_graph/cyphers/crud_cyphers.py`
- `knowledge_graph/src/insert_obs_data.py`
- new `data_pipeline/`
- new `reasoning_ontology/src/dataset.py`

## Phase 2. Learned Ontology

Do before traversal policy:

1. implement ontology encoder
2. train prototype learner
3. write ontology assignments back into memory graph

Main files:

- new `reasoning_ontology/`
- `scripts/run_classify.py`
- `knowledge_graph/src/insert_obs_data.py`
- `knowledge_graph/src/retrieve_data.py`

## Phase 3. Learned Traversal

Do after ontology exists:

1. train policy on graph candidates
2. use policy to choose paths
3. log selected paths

Main files:

- new `traversal_policy/`
- `knowledge_graph/src/retrieve_data.py`
- `agents/src/react.py`
- `agents/src/reflexion.py`

## Phase 4. Q1 Evaluation

Do once the learned modules are stable:

1. add path-grounding metrics
2. add ablations
3. add stress tests
4. add transfer evaluation

Main files:

- `eval/test/react_test.py`
- `eval/test/reflexion_test.py`
- new `eval/test/grounding_metrics.py`
- new `eval/test/stress_tests.py`

## 5. Minimum Viable Research Delta

If implementation bandwidth is limited, the smallest publishable delta from the current repo is:

1. preserve current repo as the heuristic baseline
2. implement only the learned ontology first
3. keep traversal as a reranker instead of full sequential policy
4. add grounding/path metrics and ablations

That would already support a strong paper version:

`heuristic dual-memory vs ontology-aware dual-memory`

The full proposal version is:

`heuristic dual-memory vs learned ontology vs learned traversal vs full joint model`

## 6. Immediate Next Coding Tasks

If you want to start implementation now, the best first coding backlog is:

1. Refactor current heuristic retrieval into an explicit baseline module
   - create `knowledge_graph/src/retrieve_heuristic.py`
2. Add structured retrieval output type
   - create `knowledge_graph/src/retrieval_types.py`
3. Add graph schema v2 with ontology concept nodes
   - create `knowledge_graph/cyphers/schema_v2.py`
4. Create ontology dataset builder from existing artifacts
   - create `reasoning_ontology/src/dataset.py`
5. Create ontology prototype learner skeleton
   - create `reasoning_ontology/src/prototype_learner.py`
6. Extend evaluation to store retrieved node ids and paths
   - modify `eval/test/react_test.py`
   - modify `eval/test/reflexion_test.py`

## 7. Deliverable Mapping

To align with the proposal, each promised deliverable maps to code as follows:

### Deliverable 1. Reproducible code release

- `README.md`
- `scripts/README.md`
- `scripts/run_experiment.py`

### Deliverable 2. Learned ontology module

- `reasoning_ontology/src/*`

### Deliverable 3. Learned traversal policy

- `traversal_policy/src/*`

### Deliverable 4. Grounding benchmark and metric suite

- `eval/test/grounding_metrics.py`
- `eval/test/path_metrics.py`
- `eval/test/stress_tests.py`

### Deliverable 5. Paper-ready experiment artifact package

- `experiments/`
- structured outputs from experiment runners

## 8. Bottom Line

The proposal maps very cleanly onto the current repo:

- the current symbolic classifier becomes the handcrafted-schema baseline
- the current Neo4j scoring function becomes the heuristic-traversal baseline
- the current ReAct and Reflexion runners remain the fixed execution backbone
- the new work should be concentrated in:
  - `reasoning_ontology/`
  - `traversal_policy/`
  - `knowledge_graph/`
  - `eval/`

That is the smallest code reorganization that still supports the full scientific claim of the proposal.
