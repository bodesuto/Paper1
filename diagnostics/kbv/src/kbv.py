import re
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common.logger import get_logger
from common.deepeval_models import get_deepeval_llm

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.test_case import LLMTestCaseParams

from deepeval.metrics import (
    AnswerRelevancyMetric,
    # Commenting out for now since we don't have retrieval context in pruned traces; can add back later if we do.
    # FaithfulnessMetric
)

logger = get_logger(__name__)



# -------------------------
# Parsing helpers
# -------------------------

def _first_match(pattern: str, text: str) -> str:
    m = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return (m.group(1).strip() if m else "")

def extract_question(trace: str) -> str:
    # expects: "Question: ...\n"
    return _first_match(r"^Question:\s*(.+?)\s*$", trace)

def extract_final_answer(trace: str) -> str:
    # Prefer explicit final answer
    ans = _first_match(r"^Final Answer:\s*(.+?)\s*$", trace)
    if ans:
        return ans

    # Fallback: finish_answer action input
    # matches: Action ... finish_answer ... Action Input ... <answer>
    m = re.search(r"Action\s*\d*:\s*finish_answer.*?\nAction Input\s*\d*:\s*(.+?)\s*$",
                  trace, flags=re.MULTILINE | re.DOTALL)
    if m:
        return m.group(1).strip().strip('"')

    # Fallback: last "Action Input:" line
    lines = [ln.strip() for ln in trace.splitlines() if ln.strip().lower().startswith("action input")]
    if lines:
        return lines[-1].split(":", 1)[-1].strip().strip('"')

    return ""

def extract_observations(trace: str) -> List[str]:
    # Collect all "Observation:" blocks
    obs = re.findall(r"^Observation\s*\d*:\s*(.+?)\s*$", trace, flags=re.MULTILINE)
    return [o.strip() for o in obs if o.strip()]

def build_tool_calls_from_observations(observations: List[str]) -> List[Dict[str, str]]:
    # DeepEval ToolCall expects a name; we don't have tool names in the pruned text,
    # so we set a generic name. Context metrics still work from retrieval_context.
    return [{"name": "tool", "output": o} for o in observations]


# -------------------------
# Your GEval metrics builders (unchanged logic)
# -------------------------

def build_instruction_consistency_metric(model):
    metric = GEval(
        name="Instruction_Consistency",
        criteria=(
            "Identify whether the agent behaviour follows or adheres to the user instruction. "
            "Compare the actual output with what the instruction explicitly requires."
        ),
        evaluation_steps=[
            "Step 1: Read the instructional intent from the user question.",
            "Step 2: Identify if the agent trace does not follow instruction explicitly.",
            "Step 3: Compare ACTUAL output with what instruction demands.",
            "Step 4: Determine whether the model ignored, contradicted, or deviated from the instruction.",
            "Step 5: Provide reasoning and output a binary score (1 = consistent, 0 = inconsistent)."
        ],
        model=model,
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
    )

    metric.custom_prompt_template = """
You are an expert evaluator of instruction following.

**User Instruction:**
{input}

**Model Response:**
{actual_output}

**Model Trace**
{additional_metadata[trace]}

Decide whether the model followed the instruction.

### Scoring (binary)
- **0** → The model did NOT follow the instruction (inconsistency).
- **1** → The model followed the instruction.

"""
    return metric

# Remove from final code for now since we don't have retrieval context in pruned traces; can add back later if we do.
# def build_context_consistency_metric(model):
#     metric = GEval(
#         name="Context_Consistency",
#         criteria=(
#             "Determine whether the final answer is consistent with retrieved context "
#             "found in the agent's context."
#         ),
#         evaluation_steps=[
#             "Step 1: Compare factual claims in ACTUAL output with retrieved content.",
#             "Step 2: Identify mismatches or hallucinations.",
#             "Step 3: Output binary score: 1 = consistent, 0 = inconsistency found."
#         ],
#         model=model,
#         evaluation_params=[
#             LLMTestCaseParams.ACTUAL_OUTPUT,
#             LLMTestCaseParams.RETRIEVAL_CONTEXT
#         ],
#     )

#     metric.custom_prompt_template = """
# You evaluate whether the model's answer contradicts retrieved context.

# **Model Response:**
# {actual_output}

# **Agent Trace (including Observations):**
# {retrieval_context}

# ### Task
# Check if the response contradicts ANY factual detail present in the retrieved context.

# ### Scoring
# - **0** → Contradiction found (context inconsistency)
# - **1** → No contradiction (consistent)
# """
#     return metric


def build_logical_consistency_metric(model):
    metric = GEval(
        name="Logical_Consistency",
        criteria=(
            "Identify internal logical errors or contradictions between reasoning steps "
            "in the agent's trace and the final answer."
        ),
        evaluation_steps=[
            "Step 1: Identify reasoning steps in trace (Thought sections).",
            "Step 2: Check if reasoning logically leads to final answer.",
            "Step 3: Identify invalid arithmetic, contradictions, or unsupported conclusions.",
            "Step 4: Return score: 1 = consistent, 0 = inconsistency found."
        ],
        model=model,
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
    )

    metric.custom_prompt_template = """
You evaluate the internal logical consistency of the agent.

**Model Final Answer:**
{actual_output}

**Full Trace (Thought, Action, Observation):**
{additional_metadata[trace]}

### Task
Determine whether the reasoning steps in the trace contain a contradiction, invalid step,
or incorrect logic relative to the final answer.

### Scoring
- **0** → Logical inconsistency detected (math error, invalid inference, contradiction)
- **1** → Reasoning is logically consistent.

Return ONLY 0 or 1.
"""
    return metric


# -------------------------
# DeepEval safe measure wrapper
# -------------------------

def safe_measure(metric, test_case):
    metric.measure(test_case)
    if getattr(metric, "success", None) is None:
        metric.success = True
    return metric

@dataclass
class TraceScorerConfig:
    # If ANY "good score" < threshold -> hallucinated
    hallucination_threshold: float = 0.5

def build_metrics(model) -> List[Any]:
    """
    Returns metric instances (mix of 0..1 metrics and binary 'badness' metrics).
    We'll normalize later into "good_score".
    """
    metrics = [
        AnswerRelevancyMetric(model=model),
        # Remove from final code for now since we don't have retrieval context in pruned traces; can add back later if we do.
        # FaithfulnessMetric(model=model), 
        build_instruction_consistency_metric(model=model),
        # Remove from final code for now since we don't have retrieval context in pruned traces; can add back later if we do.
        # build_context_consistency_metric(model=model),
        build_logical_consistency_metric(model=model),
    ]
    return metrics

def build_test_case_from_trace(trace_text: str) -> Tuple[LLMTestCase, Dict[str, Any]]:
    """
    We don't have gold answers; use expected_output="".
    Most metrics work fine without gold; some ignore it.
    """
    question = extract_question(trace_text)
    actual_answer = extract_final_answer(trace_text)
    observations = extract_observations(trace_text)
    tool_calls = build_tool_calls_from_observations(observations)

    context_docs = [c["output"] for c in tool_calls]
    tools_called = [ToolCall(name=t["name"]) for t in tool_calls]

    tc = LLMTestCase(
        input=question,
        actual_output=actual_answer,
        expected_output="",  # no gold
        context=context_docs,
        retrieval_context=context_docs,
        tools_called=tools_called,
        success=False,
        additional_metadata={"trace": trace_text},
    )

    meta = {
        "question": question,
        "actual_answer": actual_answer,
        "n_observations": len(observations),
    }
    return tc, meta

def score_traces(
    traces: List[str],
    output_path: str | Path,
    config: Optional[TraceScorerConfig] = None,
) -> List[Dict[str, Any]]:
    """
    Scores traces with DeepEval metrics.
    Marks hallucinated if any metric_good < 0.5.
    Saves JSON list to output_path.
    """
    config = config or TraceScorerConfig()
    model = get_deepeval_llm()
    metrics = build_metrics(model)

    results: List[Dict[str, Any]] = []

    for idx, trace in enumerate(traces):
        trace = (trace or "").strip()
        if not trace:
            continue

        # Keep only traces that have structure
        if "Thought" not in trace and "Action" not in trace and "Observation" not in trace:
            logger.debug("Skipping trace %d (no structure)", idx)
            continue

        tc, meta = build_test_case_from_trace(trace)

        metric_rows = []
        hallucinated = False
        failing_metrics = []

        for metric in metrics:
            try:
                safe_measure(metric, tc)
                raw = getattr(metric, "score", None)
                name = getattr(metric, "name", metric.__class__.__name__)

                metric_rows.append({
                    "name": name,
                    "raw_score": raw,
                    "success": getattr(metric, "success", True),
                    "reason": getattr(metric, "reason", None),
                })

                # hallucination rule: ANY good_score < threshold
                if raw is not None and raw < config.hallucination_threshold:
                    hallucinated = True
                    failing_metrics.append(name)

            except Exception as e:
                logger.exception("Metric failed (%s) on trace %d", getattr(metric, "name", "metric"), idx)
                metric_rows.append({
                    "name": getattr(metric, "name", "metric"),
                    "raw_score": None,
                    "good_score": None,
                    "success": False,
                    "reason": str(e),
                })


        results.append({
            "index": idx,
            "question": meta["question"],
            "actual_answer": meta["actual_answer"],
            "trace": trace,
            "metrics": metric_rows,
            "hallucinated": hallucinated,
            "failing_metrics": failing_metrics,
        })

        logger.info(
            "Scored trace %d | hallucinated=%s | failing=%s",
            idx, hallucinated, ",".join(failing_metrics) if failing_metrics else "-"
        )

    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info("Saved %d scored traces -> %s", len(results), output_path)
    return results


def load_traces_from_json(path: str | Path) -> List[str]:
    """
    Load traces from RCA JSON format:

    [
      {
        "question": "...",
        "trace": "...",
        "status": true/false,
        "rca": {...}
      },
      ...
    ]

    Returns only traces where status == True.
    """

    path = Path(path)

    if not path.exists():
        logger.error("Trace JSON not found: %s", path)
        return []

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Expected list of trace objects in JSON.")

    traces = []

    for item in data:
        if not isinstance(item, dict):
            continue

        # Only keep successful runs
        if not item.get("status", False):
            continue

        trace = item.get("trace", "")
        if trace and trace.strip():
            traces.append(trace.strip())

    logger.info(
        "Loaded %d successful traces from %s",
        len(traces),
        path
    )

    return traces
