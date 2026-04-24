# Q1-Grade Research Proposal

## Learning Adaptive Reasoning Ontologies and Traversal Policies for Dual-Memory Grounded LLM Agents

## 1. Executive Summary

This proposal upgrades the current `DualMemoryKG` repository from a useful engineering system into a publishable research program centered on a precise scientific claim: graph-grounded LLM agents remain brittle because they still depend on manually specified reasoning schemas and heuristic memory traversal rules. Existing dual-memory agents separate stable knowledge from past reasoning experience, but they do not learn which conceptual abstractions should organize memory or which trajectories through memory best support grounded reasoning.

The proposed research introduces a new class of dual-memory grounded agents that jointly learn:

1. an adaptive latent reasoning ontology that replaces handcrafted `intent`, `attribute`, and `entity` schemas
2. a traversal policy over a dual-memory graph that selects the most useful evidence path for a given query

The central hypothesis is that grounding should not be treated as retrieval over a fixed structure, but as a learned control problem over a structured memory space. If successful, the project will show that learned ontological structure plus learned traversal behavior reduces unsupported reasoning, improves transfer to new tasks, and yields more efficient evidence use than heuristic memory-based agents.

This proposal is designed to support a Q1-grade paper because it offers a narrow but meaningful novelty, a defensible empirical program, clear ablations, and a direct implementation path from the current codebase.

## 2. Background and Motivation

LLM agents increasingly rely on retrieval, tools, and external memory to solve multi-hop reasoning tasks. A promising design pattern is dual memory:

- semantic memory, which stores relatively stable knowledge and support evidence
- observability memory, which stores prior reasoning traces, failures, reflections, and corrective insights

The current `DualMemoryKG` repository already instantiates this idea in a practical form. It logs agent traces, performs diagnostics, stores successful and failed trajectories in a graph, and exposes ReAct and Reflexion style agents over that graph. This is a strong implementation base, but its scientific framing remains too close to systems integration. In its current form, it can support a replication or engineering paper. To support a stronger Q1 paper, the project needs a sharper mechanism-level claim.

The key limitation is that the current system still depends on:

1. fixed symbolic categories to describe reasoning structure
2. heuristic retrieval and graph traversal to access memory

These decisions are convenient, but they impose a brittle inductive bias. They assume that human-designed schema fields are aligned with the latent structure of reasoning and that similarity-based traversal is sufficient to recover the right evidence path. Both assumptions are weak under domain shift, compositional questions, noisy memory, or contradictory traces.

The proposed work addresses that gap directly.

## 3. Problem Statement

Current graph-grounded and memory-augmented LLM agents have improved access to external evidence, but their grounding pipeline remains under-learned. In practice, most systems:

- define reasoning metadata through handcrafted labels
- link memory nodes with fixed graph relations
- retrieve support via nearest-neighbor similarity or manually weighted graph walks

This produces three failure modes:

1. conceptual mismatch: the fixed schema may not reflect the true latent reasoning structure needed for a query
2. retrieval mismatch: semantically similar memory nodes may be operationally irrelevant for the reasoning path
3. grounding mismatch: the agent may answer correctly or plausibly without being adequately supported by the selected evidence path

The scientific gap is therefore:

> existing dual-memory agents do not learn the conceptual structure that organizes memory, and they do not learn the control policy that navigates memory for grounded reasoning.

## 4. Core Research Objective

The objective is to design and evaluate a dual-memory LLM agent framework that jointly learns:

1. a latent reasoning ontology for organizing queries, traces, and memory nodes
2. a traversal policy for selecting grounded evidence paths through the dual-memory graph

The framework should improve:

- answer quality
- evidence-grounded reasoning quality
- robustness under noisy or missing memory
- transfer across tasks and domains
- retrieval efficiency

## 5. Research Questions

### RQ1

Can a learned latent reasoning ontology outperform handcrafted reasoning schemas in organizing dual-memory structures for grounded LLM reasoning?

### RQ2

Can a learned traversal policy over dual-memory graphs outperform heuristic retrieval and heuristic graph traversal in multi-step reasoning tasks?

### RQ3

Does jointly learning ontology and traversal yield better transfer under distribution shift than learning either component alone?

### RQ4

Can the proposed framework reduce unsupported reasoning while preserving or improving task accuracy and retrieval efficiency?

## 6. Hypotheses

### H1

Learned latent reasoning concepts align memory organization with task demands better than handcrafted symbolic categories.

### H2

A learned traversal policy retrieves more relevant and more efficient evidence paths than similarity-only or heuristic traversal baselines.

### H3

Joint learning of ontology and traversal produces better grounding robustness than ontology-only, traversal-only, or original dual-memory baselines.

### H4

Improved grounding manifests not only as better final-answer accuracy, but also as lower unsupported reasoning rate, better path quality, and lower traversal cost.

## 7. Scientific Contribution and Novelty

The paper should be positioned around one precise claim:

> dual-memory grounding becomes substantially more reliable when both reasoning structure and memory navigation are learned from data rather than manually specified.

The expected contributions are:

### C1. Problem Reframing

A reframing of dual-memory grounding as a joint learning problem over conceptual abstraction and graph navigation.

### C2. Adaptive Reasoning Ontology

A latent ontology learner that replaces fixed `intent`, `attribute`, and `entity` labels with data-driven reasoning prototypes.

### C3. Learned Traversal Policy

A graph traversal policy that decides which memory nodes, memory types, and transitions should support the reasoning path.

### C4. Grounding-Centered Evaluation

A stronger evaluation protocol that measures unsupported reasoning, path quality, transfer robustness, and traversal efficiency, not only answer accuracy.

This is important because many recent agent papers are methodologically weak in one of two ways: either the novelty is too broad and diffuse, or the evaluation only shows end-task accuracy gains without isolating the grounding mechanism. This proposal is designed to avoid both problems.

## 8. Relation to the Current Repository

The current repository already provides four useful assets:

1. dual memory separation into successful traces and failure-oriented insights
2. graph construction and retrieval infrastructure
3. agentic baselines through ReAct and Reflexion
4. observability and evaluation plumbing

That means the research effort does not begin from zero. Instead, the repository can be treated as the prototype baseline system:

- the current dual-memory implementation becomes the reference model
- the learned ontology replaces fixed reasoning labels in classification and retrieval
- the learned traversal module replaces heuristic graph navigation
- the existing agent runners become evaluation entry points

This makes the proposal credible because the implementation path is concrete and incremental.

## 9. Proposed Technical Framework

## 9.1 System Overview

The proposed architecture contains five modules:

1. query and trace encoder
2. latent ontology learner
3. dual-memory graph constructor
4. traversal policy learner
5. LLM execution layer

The inference pipeline is:

```text
Query q
  -> Query/Trace Encoder
  -> Latent Ontology Inference
  -> Dual-Memory Graph Conditioning
  -> Traversal Policy
  -> Evidence Path P
  -> LLM Executor
  -> Final Answer y
  -> Feedback / Memory Update
```

## 9.2 Dual-Memory Graph Design

The graph contains three major node families:

### A. Semantic Memory Nodes

These represent:

- support passages
- factual knowledge items
- entity relations
- structured knowledge fragments

### B. Observability Memory Nodes

These represent:

- successful reasoning traces
- failed reasoning traces
- error analyses
- reflections or corrective insights

### C. Latent Ontology Nodes

These represent learned reasoning concepts such as:

- intent-like prototypes
- attribute-like prototypes
- entity-role prototypes
- evidence-use patterns

The graph contains heterogeneous edges including:

- semantic relation
- trace transition
- support relation
- conflict relation
- prototype membership
- relevance relation

This creates a unified memory space spanning knowledge, experience, failure patterns, and latent conceptual structure.

## 9.3 Latent Ontology Learning

### Motivation

The original repository assumes symbolic reasoning fields. These are useful for indexing, but they are brittle. They are hand-designed, dataset-sensitive, and not guaranteed to reflect actual reasoning structure.

### Proposal

We replace the fixed schema with a learned latent ontology over queries, traces, and memory nodes.

### Inputs

- user queries
- reasoning traces
- semantic memory nodes
- observability memory nodes
- local graph context

### Outputs

- prototype embeddings for latent reasoning concepts
- membership scores linking queries and memory nodes to prototypes
- ontology-conditioned node representations

### Learning Strategy

The ontology learner combines:

1. contrastive learning
   - positive pairs: queries and traces requiring similar reasoning patterns
   - negative pairs: queries and traces requiring different reasoning patterns
2. prototype induction
   - cluster or prototype-based latent concepts in embedding space
3. consistency regularization
   - similar questions should activate compatible ontology structure
4. graph-aware smoothing
   - linked memory nodes should not drift into incompatible prototype spaces without evidence

### Expected Benefit

The ontology becomes adaptive, transferable, and aligned with actual reasoning behavior rather than human-selected fields.

## 9.4 Traversal Policy Learning

### Motivation

Heuristic retrieval assumes that semantic proximity is enough. That assumption breaks in multi-hop reasoning because the best next memory node often depends on reasoning state, memory type, and prior evidence, not just static similarity.

### State Definition

At step `t`, let the traversal state be:

```text
s_t = (q, v_t, G, Z, h_t, b_t)
```

where:

- `q` is the query
- `v_t` is the current node
- `G` is the dual-memory graph
- `Z` is the ontology representation
- `h_t` is the traversal history
- `b_t` is the accumulated evidence state

### Action Space

The policy may:

- move to a connected memory node
- switch between semantic and observability memory
- request an additional failure insight
- request a supporting trace
- stop traversal

### Reward Function

The policy reward should balance correctness, grounding, and efficiency:

```text
r = alpha * AnswerCorrectness
  + beta  * GroundingQuality
  - gamma * UnsupportedReasoning
  - delta * TraversalCost
```

### Learning Strategy

The most practical first version is not pure reinforcement learning from scratch. Instead, the paper should use:

1. imitation learning from successful historical trajectories
2. lightweight policy optimization to refine beyond demonstrated traces

This makes the approach more stable and more defensible than a heavy RL design without sufficient supervision.

## 9.5 LLM Execution Layer

The LLM should be treated as the execution engine, not the main novelty. It consumes the selected evidence path and produces the answer. For a strong scientific narrative, the paper should keep:

- the prompt structure fixed
- the base LLM fixed
- the execution layer as stable as possible across baselines

This ensures that the gains can be attributed to ontology learning and traversal learning.

## 10. Formal Problem Formulation

Let:

- `q` be a query
- `G = (V, E)` be the dual-memory graph
- `Z` be the latent ontology representation
- `pi` be the traversal policy
- `P = (v_1, ..., v_k)` be the selected evidence path
- `y` be the final answer

The system computes:

```text
Z = f_ontology(q, G)
P ~ pi(P | q, G, Z)
y = f_llm(q, P)
```

The training objective is:

```text
L = L_answer
  + lambda_1 * L_grounding
  + lambda_2 * L_policy
  + lambda_3 * L_ontology
  + lambda_4 * L_efficiency
```

where:

- `L_answer` optimizes final task correctness
- `L_grounding` penalizes answers unsupported by the chosen evidence path
- `L_policy` improves path-selection behavior
- `L_ontology` encourages stable and discriminative latent concepts
- `L_efficiency` penalizes unnecessary memory hops or token usage

## 11. Experimental Program

## 11.1 Benchmark Selection

The evaluation must match the claim. The paper is about grounded multi-step reasoning, not general knowledge QA.

### Primary Datasets

- HotpotQA
- 2WikiMultihopQA or MuSiQue

These datasets are appropriate because they require:

- multi-hop evidence aggregation
- compositional reasoning
- path selection
- evidence-backed answer generation

### Secondary Robustness Sets

- StrategyQA
- Bamboogle

These are useful for stress testing unsupported reasoning, but they should not dominate the paper.

### Recommendation

Do not use MMLU as the main benchmark. Do not use GSM8K unless the paper explicitly claims cross-task transfer beyond retrieval-heavy reasoning.

## 11.2 Baselines

The baselines should be grouped by mechanism.

### Group A. Standard Agent Baselines

- ReAct
- Reflexion

### Group B. Retrieval Baselines

- vector RAG
- semantic-only memory retrieval
- GraphRAG-style graph retrieval

### Group C. Original Repository Baseline

- current DualMemoryKG with handcrafted schema and heuristic retrieval

### Group D. Proposed Variants

- learned ontology only
- learned traversal only
- learned ontology plus learned traversal

This decomposition is essential. Without it, reviewers will not know which component caused the gains.

## 11.3 Metrics

A Q1 paper here cannot rely on exact match alone.

### Core Metrics

- exact match
- F1
- answer accuracy

### Grounding Metrics

1. Unsupported Reasoning Rate
   - fraction of outputs not sufficiently supported by the selected path
2. Path Grounding Precision
   - fraction of retrieved steps that materially support the answer
3. Memory Selection Accuracy
   - correctness of selecting the appropriate memory family and node type
4. Evidence Sufficiency Rate
   - fraction of outputs supported by minimally sufficient evidence

### Robustness Metrics

- transfer drop from in-domain to out-of-domain settings
- performance under noisy or missing memory
- sensitivity to contradictory traces

### Efficiency Metrics

- traversal length
- token budget
- latency
- average number of graph hops

The proposal should explicitly define hallucination as unsupported reasoning relative to the retrieved evidence path. This definition is sharper and more scientifically useful than generic factuality scoring.

## 11.4 Ablation Studies

The paper should include at least the following ablations:

1. no ontology learning
2. no traversal learning
3. handcrafted ontology plus heuristic traversal
4. learned ontology plus heuristic traversal
5. handcrafted ontology plus learned traversal
6. no observability memory
7. no semantic memory
8. reduced ontology size
9. constrained traversal budget

These ablations answer three distinct questions:

- what does ontology learning contribute
- what does traversal learning contribute
- why are both components necessary

## 11.5 Stress Tests

The robustness program should include:

- noisy memory injection
- missing memory nodes
- contradictory or misleading traces
- long-tail question types
- retrieval budget constraints
- cross-dataset transfer

This is necessary to support a strong claim about grounded reasoning under realistic imperfections.

## 12. Expected Results

The project is expected to show:

1. better path-supported reasoning than heuristic dual-memory baselines
2. better transfer than handcrafted schema baselines
3. lower unsupported reasoning rate than standard agentic baselines
4. more efficient evidence usage than static graph traversal

Importantly, the most publishable result is not merely higher answer accuracy. The strongest result is:

> the proposed framework produces more defensible reasoning trajectories with less unsupported evidence use and better transfer under memory shift.

That is a stronger and more reviewer-resilient story than "our agent answers more questions correctly."

## 13. Threats to Validity and Mitigation

### Threat 1. Too Many Moving Parts

If ontology, policy, prompting, and LLM backbone all change together, attribution becomes weak.

Mitigation:

- freeze the base LLM
- hold prompts constant
- vary only ontology and traversal mechanisms

### Threat 2. Benchmark Mismatch

If the dataset does not require grounded path selection, the contribution becomes unconvincing.

Mitigation:

- focus on genuine multi-hop datasets
- treat auxiliary datasets as robustness tests only

### Threat 3. Weak Grounding Labels

Grounding quality is harder to annotate than final answer correctness.

Mitigation:

- use a combination of gold supporting passages, path overlap heuristics, and human spot checks
- report both automatic and audited grounding measures

### Threat 4. RL Instability

A full RL traversal learner may be unstable or expensive.

Mitigation:

- begin with imitation learning
- use lightweight policy refinement only after a supervised warm start

### Threat 5. Engineering Overload

A proposal can look strong on paper but fail because the implementation burden is too large.

Mitigation:

- stage the work so that each phase yields publishable intermediate results
- reuse the current repository as the system backbone

## 14. Implementation Roadmap

### Stage 1. Baseline Stabilization

- finalize the current Gemini-compatible repository
- standardize graph schema and memory insertion
- instrument retrieval path logging
- produce stable reproduction scripts

### Stage 2. Learned Ontology Module

- build query and trace encoders
- induce latent prototypes
- replace handcrafted reasoning labels in indexing and retrieval

### Stage 3. Learned Traversal Module

- define graph state and action space
- derive supervision from successful historical traces
- train imitation-based traversal policy

### Stage 4. Grounding Evaluation Layer

- implement unsupported reasoning metric
- implement path quality and efficiency metrics
- create stress-test harnesses

### Stage 5. Full Experimental Campaign

- run primary benchmarks
- run ablations
- run transfer and robustness evaluation
- produce tables and plots suitable for paper submission

## 15. Deliverables

The proposal should commit to the following concrete outputs:

1. a reproducible code release based on `DualMemoryKG`
2. a learned ontology module for memory-grounded agents
3. a learned traversal policy module
4. a benchmark and metric suite for grounded reasoning over dual memory
5. a paper-ready artifact package including config files, seeds, plots, and ablation tables

## 16. Recommended Paper Structure

1. Introduction
2. Related Work
3. Problem Formulation
4. Why Heuristic Dual-Memory Grounding Fails
5. Adaptive Latent Reasoning Ontology
6. Learned Traversal Policy
7. Experimental Setup
8. Main Results
9. Ablation and Robustness Analysis
10. Transfer and Efficiency Analysis
11. Limitations and Broader Discussion
12. Conclusion

## 17. Why This Proposal Is Q1-Grade

This proposal is Q1-grade not because it uses a larger model or a more complex system, but because it satisfies the criteria that strong reviewers care about:

1. a clear scientific gap
2. a precise and non-trivial mechanism-level novelty
3. a defensible evaluation story with proper ablations
4. a credible implementation path from an existing system
5. a contribution that advances understanding, not only system plumbing

The strongest version of the paper is therefore not:

> a dual-memory knowledge graph that improves retrieval for LLM agents

The strongest version is:

> a learned dual-memory grounding framework in which both reasoning ontology and memory traversal are optimized from data, producing more grounded, more transferable, and less unsupported reasoning than heuristic memory-based agents.

## 18. Final Positioning Statement

If written and executed correctly, this work can move beyond a replication of the original dual-memory idea and become a stronger paper about learned grounding mechanisms for agentic reasoning. The repository already gives the project a practical backbone. The proposed research adds the missing scientific core: learning the structure that organizes memory and learning the policy that navigates it.

That is the version of the idea most likely to survive serious Q1 review.
