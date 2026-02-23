DIAGNOSE_REACT_TRACE_PROMPT = """
You are an expert LLM run diagnostician.

You will receive a single agent trace — containing Question, Action, Observation, and Final Answer.

---
ABOUT THE ORIGINAL AGENT
- It is a ReAct-style Wikipedia agent for HotpotQA.
- Tools: `search_wikipedia(entity: str)` and `lookup_keyword(keyword: str)`.
- It uses `WikipediaAPIWrapper(top_k_results=2, lang='en')`.
- It must base reasoning ONLY on retrieved tool observations.
- It often fails when:
  * Tool calls return empty results or 404s (`retrieval_failure`).
  * Step loops or timeouts happen (`timeout`).
---

Your task:
Analyze the run and return STRICT JSON with:

{{
  "success": true|false,
  "root_cause": "one of [timeout, tool_error, retrieval_failure, query_formulation_error, no_final_answer, policy_violation, other]",
  "explanation": "1–3 concise sentences describing what happened.",
  "insights": "1–2 concise sentences suggesting how to improve the agent next time."
}}

Guidelines:
- success=true only if the final answer is arrived without any errors or inconsistencies in steps.
- If tools fail, use "retrieval_failure" or "tool_error".
- Keep explanation and insights concise and specific.

TRACE:
{trace}

Now output ONLY valid JSON.
"""
