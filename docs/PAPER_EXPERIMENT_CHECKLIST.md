# Paper Experiment Checklist

For the full Vietnamese guide, see [REPRODUCTION_GUIDE_VI.md](./REPRODUCTION_GUIDE_VI.md).
For implemented novelty/status, see [CONTRIBUTIONS_AND_STATUS_VI.md](./CONTRIBUTIONS_AND_STATUS_VI.md).
For failure recovery, see [TROUBLESHOOTING_VI.md](./TROUBLESHOOTING_VI.md).

This is the shortest paper-facing checklist after the Langfuse migration.

## Phase 0. Environment

- [ ] Activate the correct environment
- [ ] Confirm `.env` is filled
- [ ] Keep only one of `GOOGLE_API_KEY` or `GEMINI_API_KEY`
- [ ] Confirm Neo4j is running before graph steps
- [ ] Confirm Langfuse is running if trace export is needed

```powershell
python .\scripts\run_test_llm.py
```

## Phase 1. Cheap smoke validation

- [ ] Create mini data
- [ ] Run ReAct smoke
- [ ] Run Reflexion smoke

```powershell
python .\scripts\run_prepare_mini_data.py --size 3
python .\scripts\run_react_smoke.py --limit 1
python .\scripts\run_reflexion_smoke.py --limit 1
```

## Phase 2. Build the original dual-memory pipeline

- [ ] Enable Langfuse tracing
- [ ] Export traces
- [ ] Format traces
- [ ] Run RCA
- [ ] Run KBV
- [ ] Complete HIL review
- [ ] Run classification
- [ ] Insert memories into Neo4j

```powershell
python .\scripts\run_export.py
python .\scripts\run_format_trace.py
python .\scripts\run_rca.py
python .\scripts\run_kbv.py
python .\scripts\run_hil_streamlit.py
python .\scripts\run_classify.py
python .\scripts\run_insert_obs.py
```

## Phase 3. Build the proposed extensions

- [ ] Build ontology dataset
- [ ] Fit ontology prototypes
- [ ] Run learned bootstrap retrieval
- [ ] Build traversal-policy dataset
- [ ] Fit traversal policy

```powershell
python .\scripts\run_build_ontology_dataset.py
python .\scripts\run_fit_ontology_prototypes.py
python .\scripts\run_insert_obs.py
python .\scripts\run_react_learned.py
python .\scripts\run_build_policy_dataset.py --input-path .\eval\data\react_learned.csv
python .\scripts\run_fit_traversal_policy.py
```

## Phase 4. Run baselines one by one

ReAct:

- [ ] `python .\scripts\run_react_baseline.py`
- [ ] `python .\scripts\run_react_heuristic.py`
- [ ] `python .\scripts\run_react_vector_rag.py`
- [ ] `python .\scripts\run_react_graph_rag.py`
- [ ] `python .\scripts\run_react_ontology_only.py`
- [ ] `python .\scripts\run_react_traversal_only.py`
- [ ] `python .\scripts\run_react_learned.py`
- [ ] `python .\scripts\run_react_full.py`

Reflexion:

- [ ] `python .\scripts\run_reflexion_baseline.py`
- [ ] `python .\scripts\run_reflexion_heuristic.py`
- [ ] `python .\scripts\run_reflexion_vector_rag.py`
- [ ] `python .\scripts\run_reflexion_graph_rag.py`
- [ ] `python .\scripts\run_reflexion_ontology_only.py`
- [ ] `python .\scripts\run_reflexion_traversal_only.py`
- [ ] `python .\scripts\run_reflexion_learned.py`
- [ ] `python .\scripts\run_reflexion_full.py`

## Phase 5. Run paper-level suites

- [ ] Ablation suite
- [ ] Stress suite
- [ ] Transfer summary
- [ ] Result summary table

```powershell
python .\scripts\run_ablation_suite.py --agent react
python .\scripts\run_ablation_suite.py --agent reflexion
python .\scripts\run_stress_suite.py --agent react --strategy full --stress noisy --output-path .\eval\data\react_stress_noisy.csv
python .\scripts\run_transfer_eval.py --in-domain .\eval\data\ablations\react_full.csv --out-of-domain .\eval\data\reflexion_full.csv --output-path .\eval\data\transfer_summary.csv
python .\scripts\run_result_summary.py --inputs .\eval\data\ablations\react_baseline.csv .\eval\data\ablations\react_full.csv .\eval\data\ablations\reflexion_baseline.csv .\eval\data\ablations\reflexion_full.csv --output-path .\eval\data\paper_summary.csv
```

## Common failure points

- Missing `GOOGLE_API_KEY`: LLM scripts fail immediately
- Gemini `429 RESOURCE_EXHAUSTED`: free-tier quota exhausted
- Gemini `404 NOT_FOUND`: wrong model name
- Neo4j connection/index error: graph-based retrieval and insertion fail
- Missing Langfuse keys: trace export fails
- Missing prototypes: `ontology_only`, `learned`, and `full` degrade
- Missing traversal policy: `full` is not a true trained-traversal run
