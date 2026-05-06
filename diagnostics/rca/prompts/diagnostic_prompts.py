DIAGNOSE_REACT_TRACE_PROMPT = """
You are an expert LLM reasoning diagnostician specializing in grounded reasoning systems.

You will analyze a reasoning trace from an agent using a Dual-Memory Knowledge Graph. 
Your goal is to perform deep error decomposition to identify the precise failure mechanism.

---
ERROR TAXONOMY:
1. "ontology_mismatch" (E-Ont): The agent failed to identify or align with the correct reasoning concept (e.g., bridge, comparison) needed for the question.
2. "traversal_suboptimality" (E-Trav): The agent selected a suboptimal path in the Knowledge Graph or missed critical evidence nodes despite them being available.
3. "grounding_gap" (E-Gnd): The agent received the correct evidence but failed to use it, hallucinated, or contradicted the provided facts.
4. "knowledge_deficiency" (E-KB): The required evidence was not present in the Knowledge Graph (Semantic or Observability memory).
5. "reasoning_loop" (E-Loop): The agent repeated thoughts or actions without making progress.
6. "timeout" (E-Time): The agent reached the maximum step limit.
7. "success": The agent arrived at the correct answer with valid, grounded steps.

---
TASK:
Analyze the trace and return STRICT JSON:

{{
  "success": true|false,
  "root_cause": "one of [ontology_mismatch, traversal_suboptimality, grounding_gap, knowledge_deficiency, reasoning_loop, timeout, success]",
  "explanation": "1–3 sentences identifying the specific failure point.",
  "mechanism_insight": "How could the Adaptive Ontology or Traversal Policy be improved to fix this?",
  "severity": 1-5
}}

TRACE:
{trace}

Now output ONLY valid JSON.
"""
