# DualMemoryKG: A Domain-Agnostic Dual-Memory Framework for Grounded Reasoning

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-green.svg)
![Target](https://img.shields.io/badge/target-Q1_Publication-orange.svg)

**DualMemoryKG** is a research-to-production framework designed to solve the problem of hallucinations in LLMs through explicit, mathematically rigorous evidence control over a Dual-Memory Knowledge Graph (Semantic + Observability memories).

This repository has been upgraded to **Enterprise-Grade** and is specifically targeted for top-tier **Q1 Academic Publication**.

---

## 🌟 Core Breakthroughs (Q1 Contributions)

1. **Contrastive Latent Ontology Induction**: Automatically learns and separates latent reasoning strategies from behavioral traces using a contrastive prototype learning mechanism.
2. **Information-Theoretic Evidence Selection**: Models graph traversal as an uncertainty reduction problem, optimizing for *Marginal Information Gain* and penalizing redundancy, moving beyond simple similarity search.
3. **Deep Error Decomposition Framework**: Implements a scientific error taxonomy (`E-Ont`, `E-Trav`, `E-Gnd`, `E-KB`, `E-Loop`) to diagnose exact failure mechanisms, isolating true grounding from lucky hallucination.

## 🏗️ Architectural Blueprints

### 1. Macro-Architecture: The Knowledge Bridge
This diagram illustrates the separation between Continuous (Semantic) and Discrete (Symbolic) memory layers, synchronized by the Reasoning Ontology.

```mermaid
graph TD
    subgraph "Domain Layer (External)"
        D[Raw Data/Docs] --> Ingest[Ingestion Engine]
    end

    subgraph "Memory Layer (Dual Memory)"
        VDB[(ChromaDB: Vector Space)]
        KG[(Neo4j: Symbolic Space)]
    end

    subgraph "Reasoning Layer (DualMemoryKG Core)"
        Agent{Grounded Agent}
        Ontology[Reasoning Ontology - Z]
    end

    Ingest --> VDB
    Ingest --> KG
    
    Agent <--> VDB
    Agent <--> KG
    Agent --> Ontology
    Ontology -- "Refines Policy" --> Agent
```

### 2. Uncertainty-Aware Reasoning Loop
The ReAct cycle is augmented with an **Information-Theoretic Gate** that controls evidence acquisition based on Surprisal.

```mermaid
stateDiagram-v2
    [*] --> Thought: Receive Query
    
    state Thought {
        [*] --> ConceptAlignment
        ConceptAlignment --> RetrievalPlan
    }

    Thought --> Action: Retrieve Evidence
    
    state Action {
        [*] --> VectorSearch
        VectorSearch --> GraphWalk
        GraphWalk --> Pruning: "Surprisal Penalty"
    }

    Action --> Observation: Extract Facts
    Observation --> Validation: "Faithfulness Check"
    
    Validation --> Thought: "Low Confidence"
    Validation --> FinalAnswer: "Entropy Threshold Met"
    
    FinalAnswer --> [*]
```

### 3. Contrastive Latent Ontology Induction (Feed-forward)
How behavioral traces evolve into stable reasoning prototypes.

```mermaid
graph LR
    Traces[Behavioral Traces] --> Encoder[Trace Encoder]
    Encoder --> Latent[Latent Space]
    
    subgraph "Contrastive Induction"
        Latent --> Match{Prototype Matching}
        Match -- "Positive" --> Pull[Update Prototypes]
        Match -- "Negative" --> Push[Repulsion Force]
    end
    
    Push & Pull --> Ontology[Dynamic Ontology]
```

### 4. Deep Error Decomposition (RCA Engine)
The scientific diagnostic flow used to prove the **Grounding Objective**.

```mermaid
graph TD
    Fail[System Failure] --> RCA{Diagnostic Engine}
    
    RCA --> E_Ont["E-Ont: Ontology Misalignment"]
    RCA --> E_Trav["E-Trav: Traversal Gap"]
    RCA --> E_Gnd["E-Gnd: Hallucination/Grounding Error"]
    
    E_Ont --> Fix_Ont[Update Prototypes]
    E_Trav --> Fix_Policy[Adjust IG Weight]
    E_Gnd --> Fix_Temp[Reduce LLM Temperature]
```

### 5. End-to-End Grounded Reasoning Pipeline
The full journey from a raw query to a mathematically verified answer.

```mermaid
graph TD
    User([Raw Query]) --> Router{Complexity Router}
    
    subgraph "Phase 1: Knowledge Priming"
        Router -- "Complex" --> InitSearch[Vector Seed Search]
        InitSearch --> Bridge[KG Entry Points]
    end
    
    subgraph "Phase 2: Information-Theoretic Traversal"
        Bridge --> Policy{Traversal Policy}
        Policy --> Explore[Multi-hop Walk]
        Explore --> Prune{Entropy Pruning}
        Prune -- "High Surprisal" --> Select[Extract Evidence]
        Prune -- "Redundant" --> Policy
    end
    
    subgraph "Phase 3: Verified Synthesis"
        Select --> Synthesis[LLM reasoning]
        Synthesis --> Evaluator{Reflexion}
        Evaluator -- "Grounding Fail" --> RCA[Decomposition]
        RCA --> Policy
        Evaluator -- "Grounding Success" --> Output([Final Verified Answer])
    end
```

## 📁 Repository Structure (Product Standard)

```text
DualMemoryKG/
├── core/                   # (Planned) Python package root
├── agents/                 # ReAct & Reflexion implementations
├── common/                 # Pydantic-based configuration & logging
├── diagnostics/            # RCA & Error Decomposition Engine
├── docs/                   # Full academic and technical documentation
├── eval/                   # Grounding-centered metrics and summaries
├── knowledge_graph/        # Neo4j Graph schemas and queries
├── reasoning_ontology/     # Contrastive Latent Ontology Learner
├── traversal_policy/       # Uncertainty-Aware Evidence Selector
├── scripts/                # Entry points for experiments and pipelines
├── pyproject.toml          # Packaging and tooling configuration
└── .env                    # Environment variables (Pydantic validated)
```

## 🚀 Quick Start

### 1. Installation
This project is packaged for easy installation. We recommend using a virtual environment.
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### 2. Configuration
Copy `.env.example` to `.env` and configure your API keys and Neo4j credentials. 
The system uses **Pydantic** for fail-fast configuration validation.
```bash
cp .env.example .env
```

### 3. Running the Pipeline
To run a full ablation suite to generate Q1 comparative results:
```bash
python scripts/run_ablation_suite.py --agent react
```

To run the Deep Error Decomposition analysis:
```bash
python scripts/run_rca_decomposition.py --rca-json output/your_rca_results.json
```

## 📖 Documentation

All detailed academic and technical documentation has been organized in the `docs/` folder:
- **Theoretical Claims**: `docs/THEORETICAL_CLAIMS_AND_PROOF_SKETCH.md`
- **Error Diagnostics**: `docs/TROUBLESHOOTING_VI.md`
- **Reproduction Guide**: `docs/REPRODUCTION_GUIDE_VI.md`

---

*This codebase is strictly formatted using `black`, sorted with `isort`, and configured for `mypy` typing to ensure production reliability.*
