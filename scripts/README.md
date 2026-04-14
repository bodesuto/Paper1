# Scripts Module (Pipeline Runners)

The `scripts/` folder contains **entry-point scripts** that run the main pipeline stages of the repository end-to-end.

These scripts orchestrate:
- LangSmith export
- Trace formatting
- RCA / KBV diagnostics
- Human review (HIL)
- Classification
- Knowledge graph insertion
- Agent evaluation runs

---

## Files

scripts/
├── run_test_llm.py          # Simple LLM connectivity test
├── run_prepare_mini_data.py # Create tiny train/validation CSVs
├── run_react_smoke.py       # Cheap ReAct smoke test (no DeepEval)
├── run_reflexion_smoke.py   # Cheap Reflexion smoke test (no DeepEval)
├── run_export.py            # Export LangSmith runs → JSON
├── run_format_trace.py      # JSON → ReAct trace TXT
├── run_rca.py               # RCA diagnosis
├── run_kbv.py               # Knowledge based verification
├── run_hil_streamlit.py     # Launch HIL review UI
├── run_classify.py          # Classify HIL + RCA outputs
├── run_insert_obs.py        # Insert classified payloads into KG
├── run_react_agent.py       # ReAct evaluation (baseline / dual memory)
├── run_reflexion_agent.py   # Reflexion evaluation (baseline / dual memory)

---

## Typical pipeline order

Recommended execution sequence:

```bash
python scripts/run_export.py
python scripts/run_format_trace.py
python scripts/run_rca.py
python scripts/run_kbv.py

# Human review
python scripts/run_hil_streamlit.py

# After review
python scripts/run_classify.py
python scripts/run_insert_obs.py
```

## Script summary

run_export.py
Exports LangSmith project runs using export_runs() → OUTPUT_PATH JSON.

run_format_trace.py
Converts exported runs into normalized ReAct traces (.react.txt).

run_rca.py
Runs root cause analysis over traces and writes .rca.json.

run_kbv.py
Scores traces with automated KBV metrics → .kbv.json.

run_hil_streamlit.py
Initializes .hil.json (from KBV output if needed) and launches the Streamlit HIL review UI.

run_classify.py
Runs classifier over:
•	HIL results → .classified.json
•	RCA insights → .classified_insights.json

run_insert_obs.py
Combines classified HIL + RCA payloads and inserts them into Neo4j (knowledge graph).

Agent evaluation scripts
run_react_agent.py
Runs ReAct evaluation (baseline or dual memory).

run_reflexion_agent.py
Runs Reflexion evaluation (training + testing + dual memory).

Utility
run_test_llm.py
Quick sanity check that the configured LLM works.

Smoke test utilities
run_prepare_mini_data.py
Creates tiny CSV files such as `mini_train_3.csv` and `mini_validation_3.csv`.

run_react_smoke.py
Runs ReAct on a very small CSV without DeepEval or Neo4j.

run_reflexion_smoke.py
Runs Reflexion on a very small CSV without DeepEval or Neo4j.
