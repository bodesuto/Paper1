import json
import time
from types import SimpleNamespace

from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
    GEval,
)
from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.test_case import LLMTestCaseParams

from common.deepeval_models import get_deepeval_llm
from common.rate_limiter import RateLimiter

# Module-level rate limiter shared by all metric calls.
# 12 calls/min + 5s minimum delay protects Gemini API from 429 / quota errors.
_eval_limiter = RateLimiter(calls_per_minute=12, min_delay_s=5.0)


def build_instruction_inconsistency_metric(model):
    metric = GEval(
        name="Instruction_Inconsistency",
        criteria=(
            "Identify whether the agent behavior violates or ignores the user instruction. "
            "Compare the actual output with what the instruction explicitly requires."
        ),
        evaluation_steps=[
            "Step 1: Read the instructional intent from the user question.",
            "Step 2: Identify if the agent trace does not follow the instruction explicitly.",
            "Step 3: Compare the actual output with what the instruction demands.",
            "Step 4: Determine whether the model ignored, contradicted, or deviated from the instruction.",
            "Step 5: Provide reasoning and output a binary score (1 = inconsistent, 0 = consistent).",
        ],
        model=model,
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
    )

    metric.custom_prompt_template = """
You are an expert evaluator of instruction following.

User Instruction:
{input}

Model Response:
{actual_output}

Model Trace:
{additional_metadata[trace]}

Scoring:
- 0 -> The model followed the instruction.
- 1 -> The model did not follow the instruction.

Return only 0 or 1.
"""
    return metric


def build_context_inconsistency_metric(model):
    metric = GEval(
        name="Context_Inconsistency",
        criteria=(
            "Determine whether the final answer contradicts or misrepresents retrieved context "
            "found in the agent context."
        ),
        evaluation_steps=[
            "Step 1: Compare factual claims in the actual output with retrieved content.",
            "Step 2: Identify mismatches or hallucinations.",
            "Step 3: Output a binary score: 1 = inconsistency, 0 = consistent.",
        ],
        model=model,
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT,
        ],
    )

    metric.custom_prompt_template = """
You evaluate whether the model answer contradicts retrieved context.

Model Response:
{actual_output}

Retrieved Context:
{retrieval_context}

Scoring:
- 0 -> No contradiction.
- 1 -> Contradiction found.

Return only 0 or 1.
"""
    return metric


def build_logical_inconsistency_metric(model):
    metric = GEval(
        name="Logical_Inconsistency",
        criteria=(
            "Identify internal logical errors or contradictions between reasoning steps "
            "in the agent trace and the final answer."
        ),
        evaluation_steps=[
            "Step 1: Identify reasoning steps in the trace.",
            "Step 2: Check if the reasoning logically leads to the final answer.",
            "Step 3: Identify invalid arithmetic, contradictions, or unsupported conclusions.",
            "Step 4: Return 1 if inconsistency is found, otherwise 0.",
        ],
        model=model,
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
    )

    metric.custom_prompt_template = """
You evaluate the internal logical consistency of the agent.

Model Final Answer:
{actual_output}

Full Trace:
{additional_metadata[trace]}

Scoring:
- 0 -> Reasoning is logically consistent.
- 1 -> Logical inconsistency detected.

Return only 0 or 1.
"""
    return metric


def build_answer_given_metric(model):
    metric = GEval(
        name="Answer_Given",
        criteria=(
            "Determine if the expected answer is present in the actual answer. "
            "Additional context is allowed as long as the expected answer is semantically contained."
        ),
        evaluation_steps=[
            "Step 1: Extract the key entities and facts from the expected answer.",
            "Step 2: Check if the actual output contains these key entities or facts.",
        ],
        model=model,
        evaluation_params=[
            LLMTestCaseParams.EXPECTED_OUTPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
    )

    metric.custom_prompt_template = """
You are an expert evaluator of answer matching.

Expected Answer:
{expected_output}

Actual Output:
{actual_output}

Determine whether the expected answer or its key entities and facts are present in the actual output.
Formatting differences, extra punctuation, abbreviations, and extra context are acceptable.

Return only 0 or 1.
"""
    return metric


model = get_deepeval_llm()
exact_match_metric = build_answer_given_metric(model=model)


def is_bad_call(call):
    output = str(call["output"]).lower()
    if "no more results" in output:
        return True
    if "page fetch failed" in output:
        return True
    if "no readable paragraphs" in output:
        return True
    if "error" in output:
        return True
    if "404" in output:
        return True
    return False


def _parse_json_like(value, default):
    if value is None:
        return default
    if isinstance(value, (list, dict)):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
        try:
            return json.loads(value)
        except Exception:
            return default
    return default


def _memory_evidence_docs(memory_payload, retrieval_path) -> list[str]:
    payload = _parse_json_like(memory_payload, {})
    path_items = _parse_json_like(retrieval_path, [])
    docs: list[str] = []

    if isinstance(payload, dict):
        for key in ("experiences", "insights", "ontology_concepts", "selected_path", "grounding_metadata", "semantic_supports"):
            for item in payload.get(key, []) or []:
                text = str(item).strip()
                if text:
                    docs.append(text)

    for item in path_items:
        if not isinstance(item, dict):
            continue
        preview = str(item.get("text_preview", "")).strip()
        if preview:
            docs.append(preview)
        descriptor = " | ".join(
            [
                f"memory_type={item.get('memory_type')}",
                f"labels={item.get('labels', [])}",
                f"attribute_overlap={item.get('attribute_overlap', [])}",
                f"entity_overlap={item.get('entity_overlap', [])}",
                f"weak_concepts={item.get('weak_concepts', [])}",
                f"ontology_matches={item.get('ontology_matches', [])}",
                f"semantic_supports={item.get('semantic_supports', [])}",
            ]
        )
        docs.append(descriptor)

    deduped: list[str] = []
    seen: set[str] = set()
    for doc in docs:
        normalized = doc.strip()
        if normalized and normalized not in seen:
            deduped.append(normalized)
            seen.add(normalized)
    return deduped


def build_test_case(
    question: str,
    gold_answer: str,
    actual_answer: str,
    tool_calls,
    trace_text,
    retrieval_path=None,
    memory_payload=None,
    retrieval_strategy: str | None = None,
):
    tool_context_docs = [str(call["output"]) for call in tool_calls if call.get("output")]
    memory_context_docs = _memory_evidence_docs(memory_payload, retrieval_path)
    context_docs = tool_context_docs + memory_context_docs
    success_flag = gold_answer in actual_answer

    tools_called = [ToolCall(name=tool["name"]) for tool in tool_calls]

    return LLMTestCase(
        input=question,
        actual_output=actual_answer,
        expected_output=gold_answer,
        context=context_docs,
        retrieval_context=context_docs,
        tools_called=tools_called,
        success=success_flag,
        additional_metadata={
            "trace": trace_text,
            "retrieval_path": retrieval_path or [],
            "memory_payload": memory_payload or {},
            "retrieval_strategy": retrieval_strategy or "baseline",
        },
    )


answer_relevancy_metric = AnswerRelevancyMetric(model=model)
faithfulness_metric = FaithfulnessMetric(model=model)
ctx_precision_metric = ContextualPrecisionMetric(model=model)
ctx_recall_metric = ContextualRecallMetric(model=model)
ctx_relevancy_metric = ContextualRelevancyMetric(model=model)
build_instruction_inconsistency_metric = build_instruction_inconsistency_metric(model=model)
build_context_inconsistency_metric = build_context_inconsistency_metric(model=model)
build_logical_inconsistency_metric = build_logical_inconsistency_metric(model=model)


def safe_measure(metric, test_case, max_retries: int = 3):
    """Call metric.measure() with rate limiting and exponential backoff.

    - Respects global ``_eval_limiter`` to prevent Gemini API 429 errors.
    - Retries up to ``max_retries`` times on transient errors (503/429/timeout).
    - Returns a safe SimpleNamespace on permanent failure so the run continues.
    """
    _eval_limiter.wait()  # Rate limit BEFORE every DeepEval API call

    for attempt in range(max_retries):
        try:
            metric.measure(test_case)
            if getattr(metric, "success", None) is None:
                metric.success = True
            return metric
        except Exception as exc:
            err_str = str(exc).lower()
            is_transient = any(code in err_str for code in ["429", "503", "quota", "timeout", "unavailable", "rate"])

            if is_transient and attempt < max_retries - 1:
                backoff = (2 ** attempt) * 10  # 10s, 20s, 40s
                print(f"  [safe_measure] Transient error ({type(exc).__name__}). Retry {attempt+1}/{max_retries-1} in {backoff}s...")
                time.sleep(backoff)
                _eval_limiter.wait()  # Re-acquire slot after backoff
                continue

            # Permanent failure or exhausted retries
            return SimpleNamespace(
                score=0.0,
                success=False,
                reason=f"metric_error[attempt={attempt+1}]: {type(exc).__name__}: {exc}",
            )
    # Should never reach here
    return SimpleNamespace(score=0.0, success=False, reason="metric_error: max_retries exhausted")
