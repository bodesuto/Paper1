# Addressing Hallucinations in Generative AI Agents using Observability and Dual Memory Knowledge Graphs

Implementation repository for the paper:

> **Matharaarachchi et al., 2026 — Knowledge-Based Systems**  
> *Addressing Hallucinations in Generative AI Agents using Observability and Dual Memory Knowledge Graphs*  
> https://www.sciencedirect.com/science/article/pii/S0950705126002121

---

## Core Idea

This framework reduces hallucinations in agentic LLM systems using:

1. **Observability logging** 
2. **Diagnostics modules**
   - Root Cause Analysis (RCA)
   - Knowledge-Based Verification (KBV)
   - Human-In-the-Loop review (HIL)
3. **Dual Memory Knowledge Graph**
   - Experience memory (successful traces)
   - Insight memory (failure explanations)
4. **Reasoning agents**
   - ReAct
   - Reflexion

---

## Repository Structure

```

agents/               # ReAct + Reflexion agents (baseline + dual memory)
classifier/           # Intent / entity / attribute classification
diagnostics/          # RCA, KBV, HIL
eval/                 # Experimental evaluation
knowledge_graph/      # Dual memory Neo4j KG
log_transformation/   # LangSmith → ReAct trace pipeline
scripts/              # End-to-end execution scripts
common/               # Shared config, models, logging

````

---

# Setup Instructions

---
## Requirements 

* Python 3.10+ 
* Neo4j (vector index support) 
* LangSmith account 
* Azure OpenAI LLM provider configured

## Create virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

## Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Configure environment variables

Create a `.env` file following the `.env.example` file:

```
OPENAI_API_KEY=...
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=...
NEO4J_DATABASE=neo4j
LANGSMITH_PROJECT_ID=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_DEPLOYMENT_NAME=...
```
---

# Full Pipeline Execution

Below is the recommended **end-to-end workflow**.

---

## Step 1 — Export LangSmith runs

```bash
python scripts/run_export.py
```

Output:

```
output/langsmith_runs_<...>.json
```

---

## Step 2 — Convert to ReAct trace format

```bash
python scripts/run_format_trace.py
```

Output:

```
output/langsmith_runs_<...>.react.txt
```

---

## Step 3 — Run Root Cause Analysis (RCA)

```bash
python scripts/run_rca.py
```

Output:

```
output/langsmith_runs_<...>.rca.json
```

---

## Step 4 — Run Knowledge-Based Verification (KBV)

```bash
python scripts/run_kbv.py
```

Output:

```
output/langsmith_runs_<...>.kbv.json
```

---

## Step 5 — Human Review (HIL)

```bash
python scripts/run_hil_streamlit.py
```

This launches the Streamlit interface for rating traces.

Output:

```
output/langsmith_runs_<...>.hil.json
```

---

## Step 6 — Classify traces (intent, attributes, entities)

```bash
python scripts/run_classify.py
```

Outputs:

```
output/langsmith_runs_<...>.classified.json
output/langsmith_runs_<...>.classified_insights.json
```

---

## Step 7 — Insert into Dual Memory Knowledge Graph

Make sure Neo4j is running.

```bash
python scripts/run_insert_obs.py
```

This:

* Creates vector index
* Inserts embeddings
* Stores experience + insight memory

---

# Running Agents

## ReAct Baseline / Dual Memory

```bash
python scripts/run_react_agent.py
```

## Reflexion Baseline / Dual Memory

```bash
python scripts/run_reflexion_agent.py
```

---

# 📊 Evaluation

Evaluation compares:

* ReAct
* Reflexion
* ReAct + Dual Memory
* Reflexion + Dual Memory

Metrics:

* Exact match accuracy
* Relevancy
* Faithfulness
* Consistency
* Latency
* Cost

Results are written to CSV files in `eval/data` default.

---

# 📄 Citation

If you use this repository:

```
@article{matharaarachchi2026addressing,
  title={Addressing Hallucinations in Generative AI Agents using Observability and Dual Memory Knowledge Graphs},
  author={Matharaarachchi, Amali and Moraliyage, Harsha and Mills, Nishan and Gamage, Gihan and De Silva, Daswin and Manic, Milos},
  journal={Knowledge-Based Systems},
  pages={115469},
  year={2026},
  publisher={Elsevier}
}
```

