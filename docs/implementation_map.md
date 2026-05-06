# Proposal-to-Code Implementation Map

## Goal

This document maps the revised `proposal.md` into concrete code work for the current `DualMemoryKG` repository.

The new proposal is no longer framed as:

- one more domain-specific retrieval upgrade

It is now framed as:

- a `domain-agnostic dual-memory grounded reasoning architecture`

Therefore, the implementation map must answer four questions:

1. what parts of the current repository already support this architecture?
2. what parts are still single-domain or heuristic?
3. what new modules are required so the framework remains reusable beyond one domain?
4. what should be claimed now versus what remains future work?

## 1. Current Repo Role in the New Architecture

The current repository is already a strong `first instantiation` of the architecture, because it contains:

- dual-memory storage
- agent runners
- trace export and transformation
- diagnosis and HIL pipelines
- Neo4j-backed memory retrieval
- ontology prototype fitting
- learned evidence reranking and greedy evidence selection
- grounding-centered evaluation
- stress and validation utilities

This means the repo is not empty research scaffolding. It already covers:

- `memory construction`
- `weakly supervised concept induction`
- `evidence selection`
- `grounding evaluation`

What it does **not yet** fully cover is:

- explicit multi-domain adapters
- a universal domain ingestion interface
- stronger domain-agnostic calibration
- true sequential RL-style evidence policy
- formal theory artifacts beyond proposition-level framing

## 2. Architecture-to-Repo Mapping

## A. Domain Interface Layer

### Scientific role

This layer converts domain-specific raw data into a universal typed artifact schema.

### Current repo support

Partial support already exists through:

- `scripts/run_export.py`
- `scripts/run_format_trace.py`
- `log_transformation/src/log_extractor.py`
- `log_transformation/src/log_formatter.py`
- `scripts/run_rca.py`
- `scripts/run_kbv.py`
- `scripts/run_classify.py`

These modules already transform exported traces into structured artifacts, but they are still coupled to the current workflow.

### Current status

- `usable`
- but still `pipeline-specific`
- not yet a true domain adapter abstraction

### Required code work

Introduce an explicit adapter boundary so different domains can normalize into the same artifact interface.

### New modules to add

- `domain_adapters/src/base.py`
  - abstract adapter contract
- `domain_adapters/src/hotpotqa_adapter.py`
  - adapter for current QA-style experiments
- `domain_adapters/src/aiops_adapter.py`
  - adapter for diagnostic or AIOps artifacts
- `domain_adapters/src/types.py`
  - normalized artifact dataclasses
- `domain_adapters/README.md`

### Example adapter outputs

- `NormalizedQuery`
- `NormalizedEvidenceUnit`
- `NormalizedTrace`
- `NormalizedFailure`
- `NormalizedInsight`
- `NormalizedProvenance`

### Existing files to update

- `scripts/run_export.py`
- `scripts/run_format_trace.py`
- `scripts/run_classify.py`

### Claim level

After this is added, you can claim:

- `domain-adaptable ingestion layer`

Before this is added, you should only claim:

- `partially reusable artifact transformation pipeline`

## B. Universal Typed Memory Layer

### Scientific role

This is the core domain-agnostic substrate. It stores evidence and experience in a stable type system rather than domain-specific ad hoc fields.

### Current repo support

Already strong:

- `knowledge_graph/cyphers/schema_v2.py`
- `knowledge_graph/cyphers/crud_cyphers.py`
- `knowledge_graph/src/insert_obs_data.py`
- `knowledge_graph/src/build_graph_v2.py`

### Current status

The repo already supports or approximates:

- `SemanticMemory`
- `ObservabilityMemory`
- `OntologyConcept`
- richer edge types
- support/conflict/concept/traversal-oriented metadata

This is one of the strongest implemented blocks in the repo today.

### Required code work

Strengthen the schema so it is explicitly domain-agnostic.

### Concrete tasks

1. Add provenance-first node metadata
   - source domain
   - source artifact id
   - source artifact type
   - ingestion version
2. Add domain-independent typed relations
   - `DERIVED_FROM`
   - `REFINES`
   - `EVIDENCE_FOR`
3. Separate domain payload from memory payload
   - raw domain attributes should live in metadata
   - retrieval features should stay stable under domain changes

### Existing files to update

- `knowledge_graph/cyphers/schema_v2.py`
- `knowledge_graph/cyphers/crud_cyphers.py`
- `knowledge_graph/src/insert_obs_data.py`
- `knowledge_graph/src/retrieval_types.py`

### Claim level

You can already claim:

- `typed dual-memory graph with support for semantic, observability, and ontology-linked evidence`

## C. Adaptive Ontology Induction Layer

### Scientific role

This layer organizes memory by induced reasoning concepts rather than fixed labels alone.

### Current repo support

Already implemented in a first practical form:

- `reasoning_ontology/src/dataset.py`
- `reasoning_ontology/src/encoders.py`
- `reasoning_ontology/src/prototype_learner.py`
- `reasoning_ontology/src/infer.py`
- `scripts/run_build_ontology_dataset.py`
- `scripts/run_fit_ontology_prototypes.py`

### Current status

This block is currently:

- `adaptive`
- `weakly supervised`
- `prototype-based`

It is **not yet**:

- fully latent
- graph-regularized end-to-end
- domain-shared plus domain-private concept decomposition

### Required code work

The next step is not to throw this away. It is to generalize it.

### Concrete tasks

1. Add domain tags into ontology training examples
   - extend `OntologyTrainingExample`
2. Separate:
   - shared reasoning concepts
   - domain-specific concepts
3. Add concept calibration for new domains
   - lightweight adaptation head or scaling layer
4. Export concept diagnostics
   - concept frequency by domain
   - concept stability under domain changes
   - concept purity / coherence by split

### New modules to add

- `reasoning_ontology/src/domain_calibration.py`
- `reasoning_ontology/src/concept_diagnostics.py`

### Existing files to update

- `reasoning_ontology/src/dataset.py`
- `reasoning_ontology/src/prototype_learner.py`
- `reasoning_ontology/src/infer.py`
- `scripts/run_build_ontology_dataset.py`
- `scripts/run_fit_ontology_prototypes.py`

### Claim level

You can currently claim:

- `adaptive weakly supervised ontology prototypes`

You should not yet claim:

- `fully learned latent ontology model`

## D. Evidence Control Layer

### Scientific role

This layer is responsible for choosing grounded evidence, not just retrieving similar memory.

### Current repo support

Implemented across:

- `knowledge_graph/src/retrieve_heuristic.py`
- `knowledge_graph/src/retrieve_learned.py`
- `traversal_policy/src/dataset.py`
- `traversal_policy/src/train.py`
- `traversal_policy/src/infer.py`
- `traversal_policy/src/path_builder.py`
- `evidence_selector/src/objective.py`
- `evidence_selector/src/greedy_selector.py`

### Current status

The repo already has a credible first version of evidence control:

- candidate retrieval
- pairwise ranking learner
- greedy evidence selector under an explicit objective
- path logging and selected path evaluation

This is a major improvement over heuristic retrieval.

### What it really is today

It is best described as:

- `learned evidence reranking + objective-based selection`

It is not yet:

- full graph planning
- sequential decision-making over state
- offline RL

### Required code work

### Phase D1. Q1-safe strengthening

1. improve policy supervision quality
   - separate successful selected nodes from ambiguous fail cases
   - track stronger preference labels
2. log contradiction and redundancy signals at candidate level
3. export calibration curves for selected evidence scores

### Phase D2. Domain-agnostic strengthening

1. make policy features domain-stable
   - concept coverage
   - support coverage
   - evidence family diversity
   - contradiction risk
   - cost
2. decouple domain tokens from generic policy inputs

### Phase D3. Research extension

1. sequential state representation
2. offline RL or constrained policy improvement
3. stop-action learning

### New modules to add

- `traversal_policy/src/calibration.py`
- `traversal_policy/src/offline_rl.py`
- `traversal_policy/src/sequential_state.py`

### Existing files to update

- `traversal_policy/src/dataset.py`
- `traversal_policy/src/train.py`
- `traversal_policy/src/infer.py`
- `evidence_selector/src/objective.py`
- `evidence_selector/src/greedy_selector.py`

### Claim level

You can currently claim:

- `learned evidence selection under a grounding-aware objective`

You should not yet claim:

- `reinforcement-learned graph traversal policy`

## E. Grounding Verification Layer

### Scientific role

This layer tests whether the answer is supported by the selected evidence.

### Current repo support

Already present and stronger than the original repo:

- `eval/test/grounding_metrics.py`
- `eval/test/annotated_evidence.py`
- `scripts/run_prepare_evidence_annotation.py`
- `scripts/run_annotated_evidence_eval.py`
- `eval/test/result_summary.py`

### Current status

This block is in good shape for a strong empirical paper because the repo now supports:

- heuristic grounding proxies
- annotated evidence scoring
- bootstrap summaries
- paired comparison against reference runs

### Required code work

1. make annotated evidence the primary validation layer
2. integrate annotation-based metrics into final summary tables automatically
3. add support-set rather than path-only evaluation for non-sequential domains
4. add domain-specific annotation guidelines while keeping a common schema

### New modules to add

- `eval/test/support_set_metrics.py`
- `ANNOTATION_GUIDELINES_VI.md`

### Existing files to update

- `eval/test/result_summary.py`
- `eval/test/annotated_evidence.py`

### Claim level

You can already claim:

- `grounding-centered evaluation protocol with annotation-based evidence metrics`

## F. Fixed LLM Execution Layer

### Scientific role

The LLM should remain the execution engine, not the main novelty.

### Current repo support

- `common/models.py`
- `agents/src/react.py`
- `agents/src/reflexion.py`
- `agents/src/memory_prompt_formatter.py`

### Current status

This area is already sufficient for the paper if kept stable.

### Required code work

Minimal only:

1. ensure prompt inputs remain fixed across baselines
2. ensure memory payload formatting is stable under domain changes
3. log prompt-side evidence serialization consistently

### Existing files to update

- `agents/src/memory_prompt_formatter.py`
- `agents/src/react.py`
- `agents/src/reflexion.py`

### Claim level

Do not position this layer as the novelty.

## 3. Experimental Infrastructure Mapping

## A. Fair Split Protocol

### Current repo support

- `data_pipeline/split_datasets.py`
- `scripts/run_build_ontology_dataset.py`
- `scripts/run_build_policy_dataset.py`
- `scripts/run_fit_ontology_prototypes.py`
- `scripts/run_fit_traversal_policy.py`

### Current status

The repo already supports leakage-safe grouped splits.

### Required code work

1. enforce split usage in experiment runners
2. forbid accidental train-on-eval workflows by default
3. add manifest checks before running full experiments

### Existing files to update

- `scripts/run_ablation_suite.py`
- `scripts/run_theorem_experiment_suite.py`
- `scripts/run_experiment.py`

## B. Baselines and Ablations

### Current repo support

- `scripts/run_ablation_suite.py`
- `scripts/run_react_baseline.py`
- `scripts/run_react_heuristic.py`
- `scripts/run_react_vector_rag.py`
- `scripts/run_react_graph_rag.py`
- `scripts/run_react_ontology_only.py`
- `scripts/run_react_traversal_only.py`
- `scripts/run_react_learned.py`
- `scripts/run_react_full.py`

and reflexion counterparts.

### Current status

This block is already strong.

### Required code work

1. add domain-agnostic experiment presets
2. add shared reporting schema independent of domain-specific fields
3. add adapter-aware experiment manifests

### New modules to add

- `scripts/_domain_presets.py`

## C. Robustness and Domain-Agnostic Validity

### Current repo support

- `scripts/run_stress_suite.py`
- `eval/test/stress_tests.py`
- `scripts/run_transfer_eval.py`
- `eval/test/transfer_eval.py`

### Current status

Good first support is already present, but transfer is now secondary evidence rather than the central claim.

### Required code work

1. prioritize robustness settings explicitly:
   - noisy memory
   - missing memory
   - contradictory insights
   - evidence-type imbalance
2. keep optional support for transfer summaries as secondary evidence
3. add architecture-validity reporting:
   - which components are domain-bound
   - which components are domain-agnostic

### New modules to add

- `experiments/architecture_validity.py`

## D. Paper Figures and Tables

### Current repo support

- `experiments/plotting.py`
- `experiments/theorem_suite.py`
- `scripts/run_paper_figures.py`

### Current status

Useful and already publication-oriented, but the naming is ahead of the underlying theory.

### Required code work

1. keep the figure pipeline
2. rename paper-facing claims to match actual evidence
3. add architecture-validity figures
4. add error decomposition figures:
   - ontology mismatch
   - evidence selection failure
   - contradiction exposure

### New modules to add

- `scripts/run_camera_ready_tables.py`
- `experiments/error_decomposition.py`

## 4. What Is Already Publishable vs What Is Future Work

## Can be defended now

The current repo can already support a strong paper built around:

1. typed dual-memory graph
2. adaptive weakly supervised ontology prototypes
3. learned evidence reranking and selection
4. grounding-centered evaluation with annotation support
5. robustness and validation utilities

This is already stronger than a pure engineering replication paper.

## Should be positioned as near-term extension

These items are conceptually aligned but not fully implemented:

1. explicit domain adapter layer
2. shared-plus-domain-specific ontology calibration
3. stronger domain-agnostic policy inputs
4. enforced split-safe experiment execution by default

## Should be positioned as future work

These items should not be overclaimed now:

1. full latent ontology learner
2. sequential RL traversal
3. theorem-backed guarantees
4. fully validated domain-universal deployment

## 5. Recommended Phased Implementation Order

## Phase 1. Q1-Safe Consolidation

Goal:

- make the current paper scientifically honest and strong

Tasks:

1. tighten claims in docs and paper wording
2. enforce held-out experiment protocol
3. push annotated evidence evaluation into the main results path
4. keep ontology and evidence-control wording accurate

## Phase 2. Domain-Agnostic Upgrade

Goal:

- make the architecture reusable by design

Tasks:

1. add explicit `domain_adapters/`
2. standardize normalized artifact types
3. inject domain metadata into memory and ontology pipelines
4. add architecture-validity result schemas and plots

## Phase 3. Stronger Learning Mechanisms

Goal:

- move from practical learned control to stronger research novelty

Tasks:

1. domain calibration for ontology concepts
2. stronger evidence preference supervision
3. sequential evidence state modeling
4. offline RL or constrained policy improvement

## Phase 4. Manuscript-Grade Theory Support

Goal:

- strengthen theoretical defensibility without overclaim

Tasks:

1. write formal problem definition
2. write error decomposition
3. write proposition-level proof sketches
4. align experiments to each proposition

## 6. Final Implementation Thesis

The correct implementation thesis for this repository is:

> evolve `DualMemoryKG` from a domain-specific dual-memory retrieval system into a domain-agnostic grounded reasoning architecture whose core reusable components are typed memory, adaptive ontology induction, learned evidence control, and grounding verification.

That is the most defensible path toward a strong Q1 paper while staying faithful to what the code can actually support.
