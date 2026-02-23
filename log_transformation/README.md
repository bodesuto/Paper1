# Log Transformation Module (LangSmith → ReAct Trace)

This module converts **LangSmith project runs** into:
1) a **portable JSON export** of full run trees, and  
2) a **normalized ReAct-style text trace** (`Question / Thought / Action / Observation / Final Answer`) for downstream evaluation (KBV), diagnosis (RCA), and human review (HIL).

This module corresponds to the **Observability logging and graph-Based memory construction** section.
---

## Files

```
log_transformation/
└── src/
    ├── log_extractor.py   # LangSmith export → JSON
    └── log_formatter.py   # JSON export → ReAct trace TXT
```
---

## 1) log_extractor.py

Exports LangSmith project runs into a portable JSON file.

export_runs(project_id, output_path, include_stats=False, include_total_stats=False)

Creates:

```json
{
  "episodes": [...]
}
```

Usage:

```python
from log_transformation.src.log_extractor import export_runs

export_runs(
    project_id="YOUR_LANGSMITH_PROJECT_ID",
    output_path="output/langsmith_export.json",
    include_stats=False,
    include_total_stats=False,
)
```

---

## 2) `src/log_formatter.py` — Convert JSON export to ReAct trace TXT

* Loads the JSON export (`payload["episodes"]`)
* Traverses each episode’s `child_runs` chronologically
* Extracts:
  * **LLMChain text** → Thought/Action/Observation/Final Answer blocks
  * **Tool outputs** → Observation blocks
* Produces a normalized trace like:

```
Question: ...
Thought: ...
Action: ...
Action Input: ...
Observation: ...
Final Answer: ...
```

* Writes multiple traces into a single `.txt` file, separated by: ======

Usage:

```python
from log_transformation.src.log_formatter import write_react_traces

write_react_traces(
    in_json_path="output/langsmith_export.json",
    out_txt_path="output/react_traces.txt",
)
```

---

## Output formats

### JSON export

`output/langsmith_export.json`

```json
{
  "episodes": [
    {
      "id": "...",
      "run_type": "chain",
      "inputs": {...},
      "outputs": {...},
      "child_runs": [...]
    }
  ]
}
```

### ReAct trace text

`output/react_traces.txt`

```
Question: ...
Thought: ...
Action: ...
Observation: ...
Final Answer: ...

================================================================================

Question: ...
...
```

---

## How this integrates with the rest of the repo

1. **Extract LangSmith runs**
   * `log_extractor.export_runs()` → `langsmith_export.json`
2. **Format to ReAct traces**
   * `log_formatter.write_react_traces()` → `react_traces.txt`
3. **Downstream**
   * KBV metrics (automated scoring)
   * RCA (failure diagnosis)
   * HIL (human review UI)

---

## Troubleshooting

### Empty export / missing runs

* Confirm `project_id` is correct
* Confirm LangSmith credentials are configured in your environment
* Ensure your runs are actually in that project

### Trace missing observations

* Tool output may not be present in `run["outputs"]["output"]` depending on tool logging
* Some runs may not use `type == "tool"` vs `run_type == "tool"` (compat layer can be added)

### Trace lacks `Final Answer`

* Some agents may end without an explicit final marker.
* Downstream modules should handle fallback extraction (e.g., last action input).

