# Run Order

> [!IMPORTANT]
> For the latest high-reliability experimental pipeline (10,000 queries), use: [**EXPERIMENT_GUIDE_V2.md**](../EXPERIMENT_GUIDE_V2.md)

For the full Vietnamese guide, see [REPRODUCTION_GUIDE_VI.md](./REPRODUCTION_GUIDE_VI.md).
For implemented novelty/status, see [CONTRIBUTIONS_AND_STATUS_VI.md](./CONTRIBUTIONS_AND_STATUS_VI.md).
For failure recovery, see [TROUBLESHOOTING_VI.md](./TROUBLESHOOTING_VI.md).

## Goal

This file gives the shortest practical order to run the repository after the Langfuse migration.

## 0. Environment Check

Optional UI:

```powershell
python .\scripts\run_control_panel.py
```

Then open `http://127.0.0.1:8787`.

Basic connectivity:

```powershell
python .\scripts\run_test_llm.py
```

If this fails:

- check `.env`
- set either `GOOGLE_API_KEY` or `GEMINI_API_KEY`
- if both are set, `GOOGLE_API_KEY` wins
- verify the correct conda env is active

## 1. Cheap Smoke Test

```powershell
python .\scripts\run_prepare_mini_data.py --size 3
python .\scripts\run_react_smoke.py --limit 1
python .\scripts\run_reflexion_smoke.py --limit 1
```

Expected:

- `.\eval\data\mini_train_3.csv`
- `.\eval\data\mini_validation_3.csv`

## 2. Start Local Services

Neo4j:

```powershell
docker compose up -d
```

Optional Langfuse:

```powershell
docker compose --profile langfuse up -d
```

If you want tracing/export, set in `.env`:

- `LANGFUSE_TRACING_ENABLED=true`
- `LANGFUSE_HOST=http://localhost:3000`
- `LANGFUSE_PUBLIC_KEY=...`
- `LANGFUSE_SECRET_KEY=...`

## 3. Export Trace Data

First make sure you have already generated some traces by running at least one smoke or experiment script with tracing enabled.

Then run:

```powershell
python .\scripts\run_export.py
```

Expected:

- `OUTPUT_PATH` exists
- usually `.\output\langfuse_export.json`

If missing:

- check `LANGFUSE_HOST`
- check `LANGFUSE_PUBLIC_KEY`
- check `LANGFUSE_SECRET_KEY`

## 4. Format ReAct Traces

```powershell
python .\scripts\run_format_trace.py
```

Expected:

- `.\output\langfuse_export.react.txt`

## 5. RCA

```powershell
python .\scripts\run_rca.py
```

Expected:

- `.\output\langfuse_export.rca.json`

## 6. KBV

```powershell
python .\scripts\run_kbv.py
```

Expected:

- `.\output\langfuse_export.kbv.json`

## 7. Human Review

```powershell
python .\scripts\run_hil_streamlit.py
```

Expected:

- `.\output\langfuse_export.hil.json`

## 8. Classification

```powershell
python .\scripts\run_classify.py
```

Expected:

- `.\output\langfuse_export.classified.json`
- `.\output\langfuse_export.classified_insights.json`

## 9. Insert into Neo4j

```powershell
python .\scripts\run_insert_obs.py
```

Expected:

- graph insertion completes
- Neo4j now contains trace/question/memory evidence nodes

## 10. Build Ontology Prototypes

```powershell
python .\scripts\run_build_ontology_dataset.py
python .\scripts\run_fit_ontology_prototypes.py
python .\scripts\run_insert_obs.py
```

Expected:

- `.\output\langfuse_export.ontology_dataset.json`
- `.\output\langfuse_export.ontology_prototypes.json`

## 11. Bootstrap Traversal Policy

```powershell
python .\scripts\run_react_learned.py
python .\scripts\run_build_policy_dataset.py --input-path .\eval\data\react_learned.csv
python .\scripts\run_fit_traversal_policy.py
```

Expected:

- `.\eval\data\react_learned.csv`
- `.\output\langfuse_export.traversal_policy_dataset.json`
- `.\output\langfuse_export.traversal_policy.json`

## 12. Run Baselines Individually

ReAct:

```powershell
python .\scripts\run_react_baseline.py
python .\scripts\run_react_heuristic.py
python .\scripts\run_react_vector_rag.py
python .\scripts\run_react_graph_rag.py
python .\scripts\run_react_ontology_only.py
python .\scripts\run_react_traversal_only.py
python .\scripts\run_react_learned.py
python .\scripts\run_react_full.py
```

Reflexion:

```powershell
python .\scripts\run_reflexion_baseline.py
python .\scripts\run_reflexion_heuristic.py
python .\scripts\run_reflexion_vector_rag.py
python .\scripts\run_reflexion_graph_rag.py
python .\scripts\run_reflexion_ontology_only.py
python .\scripts\run_reflexion_traversal_only.py
python .\scripts\run_reflexion_learned.py
python .\scripts\run_reflexion_full.py
```

## 13. Paper-Level Suites

```powershell
python .\scripts\run_ablation_suite.py --agent react
python .\scripts\run_ablation_suite.py --agent reflexion
python .\scripts\run_stress_suite.py --agent react --strategy full --stress noisy --output-path .\eval\data\react_stress_noisy.csv
python .\scripts\run_transfer_eval.py --in-domain .\eval\data\ablations\react_full.csv --out-of-domain .\eval\data\reflexion_full.csv --output-path .\eval\data\transfer_summary.csv
python .\scripts\run_result_summary.py --inputs .\eval\data\ablations\react_baseline.csv .\eval\data\ablations\react_full.csv .\eval\data\ablations\reflexion_baseline.csv .\eval\data\ablations\reflexion_full.csv --output-path .\eval\data\paper_summary.csv
```

## Mini-First Shortcut

If you want the lowest-risk order:

1. `run_test_llm.py`
2. `run_prepare_mini_data.py`
3. `run_react_smoke.py`
4. `run_reflexion_smoke.py`
5. mini baseline experiments
6. Neo4j startup
7. Langfuse tracing/export
8. graph insertion
9. ontology + traversal
10. full ablation and summary
