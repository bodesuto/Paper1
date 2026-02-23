# Diagnostics Module: Validation Pipeline (RCA → KBV → HIL)

## Overview

The **Diagnostics module** implements the paper’s **three-stage, cascading validation pipeline** used to decide which agent traces are safe to persist into **observability memory** (the KG of execution traces). The pipeline is explicitly designed to **prioritize precision over recall**: it is better to discard uncertain traces than to store potentially incorrect ones. 

**Stages (in order):**
1. **RCA** — Root-Cause Analysis & feedback
2. **KBV** — Knowledge-Based Verification (automatic hallucination checks)
3. **HIL** — Human-in-the-Loop review (expert rating)

This module’s outputs support:
- **Filtering**: preventing unreliable traces from entering the KG
- **Diagnostics**: attaching root-cause labels + explanations to traces for later reuse
- **Selective oversight**: surfacing ambiguous/high-impact traces for human review 

This module corresponds to the **Validation pipeline for memory-augmented agent planning** section.

## Directory Structure

```

diagnostics/
├── README.md
├── rca/
│   ├── src/rca.py
│   └── prompts/diagnostic_prompts.py
├── kbv/
│   └── src/kbv.py
└── hil/
├── src/app.py        # Streamlit UI
└── src/storage.py    # JSON read/atomic write helpers

```


## Usage Examples

option 1. Use the scripts `scripts/run_rca.py`, `scripts/run_kbv.py`, and `scripts/run_hil_streamlit.py`.

```
scripts/run_rca.py
scripts/run_kbv.py
scripts/run_hil_streamlit.py
```
