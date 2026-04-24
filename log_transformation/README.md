# Log Transformation Module (Langfuse -> ReAct Trace)

This module converts Langfuse traces into:
1. a portable JSON export of full trace trees, and
2. a normalized ReAct-style text trace for downstream RCA, KBV, and human review.

The downstream pipeline shape is intentionally kept stable through the `episodes` JSON format so the rest of the repo can keep working after the migration away from the legacy tracing backend.

## Files

```text
log_transformation/
`-- src/
    |-- log_extractor.py   # Langfuse export -> JSON
    `-- log_formatter.py   # JSON export -> ReAct trace TXT
```

## 1. Export traces

`log_extractor.export_runs(project_id, output_path, include_stats=False, include_total_stats=False)`

This function now reads traces from Langfuse using the configured SDK client and writes:

```json
{
  "episodes": [...]
}
```

Example:

```python
from log_transformation.src.log_extractor import export_runs

export_runs(
    project_id="paper1",
    output_path="output/langfuse_export.json",
    include_stats=False,
    include_total_stats=False,
)
```

Required environment variables:

- `LANGFUSE_HOST`
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`

Optional:

- `LANGFUSE_TRACING_ENABLED`
- `LANGFUSE_ENVIRONMENT`
- `LANGFUSE_RELEASE`
- `LANGFUSE_TRACE_NAME`

## 2. Convert JSON export to ReAct trace text

`log_formatter.write_react_traces(in_json_path, out_txt_path)`

It:

- loads `payload["episodes"]`
- traverses each episode's `child_runs` chronologically
- extracts thought/action/observation/final answer blocks
- writes a normalized ReAct-style text file

Example:

```python
from log_transformation.src.log_formatter import write_react_traces

write_react_traces(
    in_json_path="output/langfuse_export.json",
    out_txt_path="output/langfuse_export.react.txt",
)
```

## Output formats

JSON export:

`output/langfuse_export.json`

ReAct trace text:

`output/langfuse_export.react.txt`

## Pipeline integration

1. Export Langfuse traces with `run_export.py`
2. Format them with `run_format_trace.py`
3. Run downstream diagnosis and review:
   - RCA
   - KBV
   - HIL
   - classification
   - graph insertion

## Troubleshooting

### Empty export or missing traces

- Check `project_id`
- Check `LANGFUSE_HOST`
- Check `LANGFUSE_PUBLIC_KEY`
- Check `LANGFUSE_SECRET_KEY`
- Confirm traces were actually written to that Langfuse project

### Trace missing observations

- Tool output may be absent or logged under a different observation shape
- Some agent/tool spans may not populate a final text output field

### No final answer block

- Some runs do not emit an explicit final marker
- Downstream code should fall back to the last available answer-like output
