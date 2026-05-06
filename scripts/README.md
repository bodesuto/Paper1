# Scripts Module (Pipeline Runners)

Detailed Vietnamese docs:

- [REPRODUCTION_GUIDE_VI.md](../REPRODUCTION_GUIDE_VI.md)
- [CONTRIBUTIONS_AND_STATUS_VI.md](../CONTRIBUTIONS_AND_STATUS_VI.md)
- [TROUBLESHOOTING_VI.md](../TROUBLESHOOTING_VI.md)

The `scripts/` folder contains entry-point runners for the main repo workflows:

- Langfuse trace export
- trace formatting
- RCA / KBV diagnostics
- human review
- classification
- Neo4j graph insertion
- baseline, ablation, stress, and transfer experiments

## Important entry points

- `run_test_llm.py`: quick Gemini connectivity check
- `run_control_panel.py`: launch a local web UI with task queue, live logs, cancel controls, `.env` editing, CSV result dashboard, and artifact browser so the repo can be operated without typing each command manually
- `run_prepare_mini_data.py`: create tiny train/validation CSVs
- `run_react_smoke.py`: cheap ReAct smoke test without DeepEval
- `run_reflexion_smoke.py`: cheap Reflexion smoke test without DeepEval
- `run_build_ontology_dataset.py`: build ontology-training data from classified artifacts
- `run_fit_ontology_prototypes.py`: fit ontology prototypes on the train split by default
- `run_build_policy_dataset.py`: convert retrieval logs into traversal-policy episodes and save leakage-safe splits
- `run_fit_traversal_policy.py`: fit lightweight traversal policy weights on the train split by default
- `run_experiment.py`: unified explicit experiment runner
- `run_ablation_suite.py`: run baseline and retrieval ablations
- `run_stress_suite.py`: run memory perturbation stress tests
- `run_transfer_eval.py`: summarize in-domain vs out-of-domain results
- `run_result_summary.py`: aggregate result CSVs into a paper table
- `run_prepare_evidence_annotation.py`: bootstrap an evidence-annotation template from result CSVs
- `run_annotated_evidence_eval.py`: score result CSVs against manual evidence annotations, including support-set metrics
- `run_architecture_validity.py`: generate a paper-facing architecture-validity and error-decomposition report
- `run_paper_figures.py`: generate publication-style PNG figures from summary/result CSVs
- `run_theorem_experiment_suite.py`: run the paper-facing experiment suite with summary, stress, transfer, optional evidence eval, and figures
- `run_export.py`: export Langfuse traces -> JSON
- `run_format_trace.py`: JSON -> ReAct trace TXT
- `run_rca.py`: RCA diagnosis
- `run_kbv.py`: knowledge-based verification
- `run_hil_streamlit.py`: launch HIL review UI
- `run_classify.py`: classify HIL + RCA outputs
- `run_insert_obs.py`: insert classified payloads into Neo4j

## Typical pipeline order

```powershell
python .\scripts\run_export.py
python .\scripts\run_format_trace.py
python .\scripts\run_rca.py
python .\scripts\run_kbv.py
python .\scripts\run_hil_streamlit.py
python .\scripts\run_classify.py
python .\scripts\run_insert_obs.py
python .\scripts\run_build_ontology_dataset.py
python .\scripts\run_fit_ontology_prototypes.py
python .\scripts\run_insert_obs.py
python .\scripts\run_experiment.py --agent react --mode dual_memory --strategy learned --output-path .\eval\data\react_learned_bootstrap.csv
python .\scripts\run_build_policy_dataset.py --input-path .\eval\data\react_learned_bootstrap.csv
python .\scripts\run_fit_traversal_policy.py
python .\scripts\run_stress_suite.py --agent react --strategy full --stress noisy --output-path .\eval\data\react_stress_noisy.csv
python .\scripts\run_transfer_eval.py --in-domain .\eval\data\react_full.csv --out-of-domain .\eval\data\react_otherdomain.csv --output-path .\eval\data\react_transfer_summary.csv
python .\scripts\run_result_summary.py --inputs .\eval\data\ablations\react_baseline.csv .\eval\data\ablations\react_full.csv --output-path .\eval\data\react_summary.csv
```

## Notes

- `run_prepare_mini_data.py` can bootstrap the required HotpotQA bridge/hard CSVs if they are missing.
- The repo accepts either `GOOGLE_API_KEY` or `GEMINI_API_KEY`; if both are present, `GOOGLE_API_KEY` is used as the primary alias.
- `ALLOW_DEFAULT_EXAMPLE_PADDING=false` is the paper-safe setting; it prevents hidden fallback few-shot padding in dual-memory runs.
- `run_result_summary.py --reference ...` now computes paired bootstrap delta confidence intervals against a baseline CSV.
- `run_prepare_evidence_annotation.py` writes annotator-friendly JSON with candidate and selected retrieval paths.
- `run_annotated_evidence_eval.py` produces evidence precision/recall/F1, support-set metrics, sufficient-set coverage, and contradiction exposure from gold annotations.
- `run_experiment.py`, `run_ablation_suite.py`, `run_stress_suite.py`, and `run_theorem_experiment_suite.py` now guard against accidentally evaluating on a `train` split unless you explicitly pass `--allow-train-eval`.

## Retrieval strategies

- `heuristic`: original symbolic + vector baseline
- `vector_rag`: dense retrieval baseline
- `graph_rag`: graph-aware proxy baseline
- `ontology_only`: ontology-aware reranking without trained traversal
- `traversal_only`: traversal policy over heuristic candidates
- `learned`: ontology-aware reranking plus traversal policy interface
- `full`: strongest learned mode, meaningful after traversal policy training

## One-command baseline scripts

ReAct:

- `python .\scripts\run_react_baseline.py`
- `python .\scripts\run_react_heuristic.py`
- `python .\scripts\run_react_vector_rag.py`
- `python .\scripts\run_react_graph_rag.py`
- `python .\scripts\run_react_ontology_only.py`
- `python .\scripts\run_react_traversal_only.py`
- `python .\scripts\run_react_learned.py`
- `python .\scripts\run_react_full.py`

Reflexion:

- `python .\scripts\run_reflexion_baseline.py`
- `python .\scripts\run_reflexion_heuristic.py`
- `python .\scripts\run_reflexion_vector_rag.py`
- `python .\scripts\run_reflexion_graph_rag.py`
- `python .\scripts\run_reflexion_ontology_only.py`
- `python .\scripts\run_reflexion_traversal_only.py`
- `python .\scripts\run_reflexion_learned.py`
- `python .\scripts\run_reflexion_full.py`
