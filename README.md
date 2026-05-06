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
