# Agents Module: Dual Memory Integrated Architecture

## Overview

The **Agents module** implements an advanced reasoning framework that combines two complementary approaches:

1. **ReAct (Reasoning + Acting)**: A single-pass agent that interleaves thought processes with tool execution ([Paper](https://arxiv.org/abs/2210.03629))
2. **Reflexion**: A two-pass agent that improves upon initial outputs through meta-reasoning and reflection ([Paper](https://arxiv.org/abs/2303.11366))

These agents are further enhanced with **Observability Memory** ([Paper](https://www.sciencedirect.com/science/article/pii/S0950705126002121)) - Learning from agent's own success, mistakes and corrections

---

## Core Components

### 1. ReAct Agent (`src/react.py`)

**Purpose**: Implements the Reasoning + Acting pattern where an agent iteratively:
1. **Thinks** about the problem and next steps
2. **Acts** by calling tools (Wikipedia search, keyword lookup)
3. **Observes** the results and repeats until reaching a final answer

**Key Functions**:
- `create_react_agent()`: Creates and executes a ReAct agent with proper tool integration
  - Configures Wikipedia search and keyword lookup tools

**Workflow**:
```
Input Query
    ↓
[Thought: Planning next step]
    ↓
[Action: Call tool (search_wikipedia / lookup_keyword)]
    ↓
[Observation: Process tool output]
    ↓
[Repeat or Final Answer]
```

**Example Usage**:
```python
from agents.src.react import create_react_agent
from agents.prompts.hotpot_examples import react_examples

agent = create_react_agent()
answer = agent.invoke({"input": "What is the capital of France?", "examples": react_examples})
```

---

### 2. Reflexion Agent (`src/reflexion.py`)

**Purpose**: Implements a two-pass reasoning approach where:

**Pass 1 - Initial Attempt**: 
- ReAct agent executes reasoning and tool calls
- Produces an initial answer

**Pass 2 - Reflection & Refinement**:
- Agent reflects on their first attempt
- Identifies mistakes or gaps in reasoning
- Leverages the previous answer as context
- Produces an improved final answer

**Key Functions**:
- `reflexion_agent_run()`: Orchestrates the two-pass flow
  - **Argument**: `agent` - A pre-configured ReAct agent instance
  - Returns final answer after reflection-driven refinement

**Workflow**:
```
Input Query
    ↓
[PASS 1: ReAct Agent - Initial Attempt]
    ├─ Thought → Action → Observation
    ├─ Thought → Action → Observation
    └─ Initial Answer
    ↓
[PASS 2: Reflection & Refinement]
    ├─ Agent reflects: "What went wrong? What did I miss?"
    ├─ Rewrites prompt with criticism of first attempt
    ├─ ReAct agent executes again with improved context
    └─ Final Refined Answer
```

**Example Usage**:
```python
from agents.src.reflexion import reflexion_agent_run
from agents.prompts.hotpot_examples import react_examples

refined_answer = reflexion_agent_run(question, examples=react_examples)
```

**Why This Works**: Agents benefit from "second chances" - reflecting on mistakes and reconsidering the problem often leads to better outputs, similar to human reasoning processes.

---

## Dual Memory Integration

### What is Dual Memory?

**Dual Memory** augments both ReAct and Reflexion agents with two complementary memory systems:

```
┌─────────────────────────────────────────────────────┐
│         Agent (ReAct or Reflexion)                  │
│                                                     │
│  ┌─────────────────────────────────────────────┐    │
│  │      Observability Memory                   │    │
│  │  • Agent's self-reflections on past runs    │    │
│  │  • Mistakes identified and corrections made │    │
│  │  • Improves through self-awareness          │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

### How Dual Memory Works Together

1. **Memory Retrieval Phase**:
   ```python
   memories = retrieve_memories(query)
   # Returns: [reasoning_trace_1, reasning_trace_2, ...]
   ```

2. **Enhanced ReAct with Dual Memory**:
   ```
   Input Query + Retrieved Memories
            ↓
   [ReAct Agent - Informed by Past Experiences]
            ↓
   Answer
   ```
   - Agent sees up to 3 similar past Q&A pairs
   - Uses them as reference for improved reasoning
   - May choose to follow similar reasoning paths or improve upon them

3. **Enhanced Reflexion with Dual Memory**:
   ```
   Input Query + Retrieved Memories
            ↓
   [PASS 1: ReAct - Informed by Past Experiences]
            ↓
   [PASS 2: Reflection - Leverages both memories + first attempt]
            ↓
   Final Answer
   ```
   - First pass: sees relevant past experiences in system prompt
   - Second pass: reflects on first attempt 

---

## Directory Structure

```
agents/
├── README.md                    # This file
├── src/
│   ├── react.py               # ReAct agent implementation
│   └── reflexion.py           # Reflexion agent implementation
└── prompts/
    ├── hotpot_prompts.py      # ReAct system prompts
    └── hotpot_examples.py     # Few-shot examples for agents
```

---

## Usage Examples

### Dual Memory ReAct Agent

```python
from agents.src.react import create_react_agent
from knowledge_graph.src.retrieve_data import retrieve_memories

query = "What is photosynthesis?"
memories = retrieve_memories(query)

agent = create_react_agent() 
answer = agent.invoke({"input": query, "examples": memories})["output"]
print(answer)
```

### Dual Memory Reflexion Agent

```python
from agents.src.reflexion import reflexion_agent_run
from knowledge_graph.src.retrieve_data import retrieve_memories

memories = retrieve_memories(query)
query = "Compare photosynthesis and cellular respiration and explain their relationship"

answer = reflexion_agent_run(agent, query)
actual_answer, debug_info = reflexion_agent_run(query, examples=memories)
print(actual_answer)
```

