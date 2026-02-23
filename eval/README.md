# Evaluation Module: Dual Memory Approach Assessment

## Overview

The **Evaluation module** provides comprehensive metrics and testing infrastructure for assessing the **Dual Memory Integrated Agent architecture**. It enables rigorous comparison of:

1. **Baseline ReAct Agent**: Single-pass reasoning with tools
2. **Baseline Reflexion Agent**: Two-pass reasoning with self-reflection
3. **Dual Memory ReAct**: ReAct augmented with dual memory knowledge graph experiences
4. **Dual Memory Reflexion**: Reflexion augmented with dual memory knowledge graph experiences + self-reflection

This module corresponds to the **Stage 1: Evaluating the impact of observability memory** section.

## Test Functions & Workflows

### Test 1: Baseline ReAct Evaluation

**Function**: `react_test.test(data_path, output_path)`

**Purpose**: Evaluate standard ReAct agent without dual memory augmentation.

**Process**:
```python
from eval.test.react_test import test

test(
    data_path="eval/data/hard_bridge_500_validation.csv",
    output_path="output/react_baseline_results.csv"
)
```

**Workflow**:
1. Load test dataset (HotpotQA questions)
2. For each question:
   - Initialize ReAct agent with trace capture
   - Run agent.invoke(question)
   - Extract final answer from trace
   - Evaluate with hallucination metrics
   - Track token usage and latency
3. Save results to CSV with all metrics

**Output Columns**:
```
index, question, gold_answer, actual_answer,
exact_match, exact_match_eval, bad_calls, total_calls, agent_latency_s,
prompt_tokens, completion_tokens, total_tokens, llm_calls, cost_usd,
answer_relevancy_score, answer_relevancy_reason,
faithfulness_score, faithfulness_reason,
instruction_inconsistency_score, instruction_inconsistency_reason,
context_inconsistency_score, context_inconsistency_reason,
logical_inconsistency_score, logical_inconsistency_reason
```

### Test 2: Baseline Reflexion Evaluation

**Function**: `reflexion_test.test(data_path, output_path)`

**Purpose**: Evaluate Reflexion agent (two-pass with self-reflection) without dual memory.

**Process**:
```python
from eval.test.reflexion_test import test

test(
    data_path="eval/data/hard_bridge_500_validation.csv",
    output_path="output/reflexion_baseline_results.csv"
)
```

**Workflow**:
1. Load test dataset
2. For each question:
   - Create ReAct agent instance
   - Call reflexion_agent_run(question, agent=agent)
   - Reflexion returns refined answer after PASS 1 + PASS 2
   - Evaluate refined answer with all hallucination metrics
   - Track combined latency (both passes)
3. Save results to CSV

### Test 3: Dual Memory ReAct Evaluation

**Function**: `react_test.test_dual_memory(data_path, output_path)`

**Purpose**: Evaluate ReAct agent **augmented with dual memory knowledge graph**.

**Process**:
```python
from eval.test.react_test import test_dual_memory

test_dual_memory(
    data_path="eval/data/hard_bridge_500_validation.csv",
    output_path="output/react_dual_memory_results.csv"
)
```

**Output Columns** (includes separate latencies):
```
memory_latency_s, agent_latency_s, total_latency_s
[all other columns same as ReAct baseline]
```

### Test 4: Dual Memory Reflexion Evaluation

**Function**: `reflexion_test.test_dual_memory(data_path, output_path)`

**Purpose**: Evaluate **Reflexion agent augmented with dual memory**.

**Process**:
```python
from eval.test.reflexion_test import test_dual_memory

test_dual_memory(
    data_path="eval/data/hard_bridge_500_validation.csv",
    output_path="output/reflexion_dual_memory_results.csv"
)
```
---

## Running Complete Evaluation Suite

### Workflow: Full Evaluation Pipeline

```bash
# Setup

# 1. Run all 4 agent configurations
python scripts/run_react_agent.py 
python scripts/run_reflexion_agent.py 
```

## Directory Structure

```
eval/
├── README.md                           # This file
├── data/
│   ├── hard_bridge_500_train.csv      # Training dataset
│   ├── hard_bridge_500_validation.csv # Evaluation dataset
│   └── load_data.py                   # Data loading utilities
│
└── test/
    ├── matrics.py                      # hallucination evaluation metrics
    ├── react_test.py                   # ReAct agent tests (baseline + dual memory)
    ├── reflexion_test.py               # Reflexion tests (baseline + dual memory)
    └── utils.py                        # Helper functions (trace capture, DB sessions)
```
