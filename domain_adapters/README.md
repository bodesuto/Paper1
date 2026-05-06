# Domain Adapters

This package introduces the first explicit `domain interface layer` for the repository.

Its purpose is to normalize domain-specific artifacts into a stable typed schema before:

- ontology induction
- memory insertion
- evidence control
- grounding evaluation

## Why this exists

The current repository already transforms traces and evaluation artifacts, but those flows are still tied to the current pipeline.

The adapter layer creates a cleaner architectural boundary:

- domain-specific parsing happens here
- domain-agnostic reasoning happens downstream

## Current contents

- `src/types.py`
  - normalized artifact dataclasses
- `src/base.py`
  - adapter interface
- `src/hotpotqa_adapter.py`
  - adapter for QA-style CSV rows
- `src/aiops_adapter.py`
  - adapter for diagnostic JSON artifacts

## Current scope

This package is an initial scaffold.

It is intended to:

- standardize artifact shape
- reduce future coupling
- support multi-domain experiments

It is not yet fully integrated into all scripts.

## Planned integration points

- `scripts/run_export.py`
- `scripts/run_format_trace.py`
- `scripts/run_classify.py`
- `knowledge_graph/src/insert_obs_data.py`
- future cross-domain experiment runners
