import os

from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.models import AzureOpenAIModel

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    GEval,
)
from deepeval.test_case import LLMTestCaseParams
from common.config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME, AZURE_OPENAI_ENDPOINT


def build_instruction_inconsistency_metric(model):
    """
    Detects when the agent does not follow the instruction in the input prompt.
    Example: User asks to TRANSLATE but the agent ANSWERS instead.
    """

    metric = GEval(
        name="Instruction_Inconsistency",
        criteria=(
            "Identify whether the agent behaviour violates or ignores the user instruction. "
            "Compare the actual output with what the instruction explicitly requires."
        ),
        evaluation_steps=[
            "Step 1: Read the instructional intent from the user question.",
            "Step 2: Identify if the agent trace does not follow instruction explicitly.",
            "Step 3: Compare ACTUAL output with what instruction demands.",
            "Step 4: Determine whether the model ignored, contradicted, or deviated from the instruction.",
            "Step 5: Provide reasoning and output a binary score (1 = inconsistent, 0 = consistent)."
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
- **0** → The model followed the instruction.
- **1** → The model did NOT follow the instruction (inconsistency).

Return ONLY a number 0 or 1.
"""
    return metric

def build_context_inconsistency_metric(model):
    """
    Detects when the final answer contradicts retrieved context shown in the trace.
    """

    metric = GEval(
        name="Context_Inconsistency",
        criteria=(
            "Determine whether the final answer contradicts or misrepresents retrieved context "
            "found in the agent's context."
        ),
        evaluation_steps=[
            "Step 1: Compare factual claims in ACTUAL output with retrieved content.",
            "Step 2: Identify mismatches or hallucinations.",
            "Step 3: Output binary score: 1 = inconsistency, 0 = consistent."
        ],
        model=model,
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT
        ],
    )

    metric.custom_prompt_template = """
You evaluate whether the model's answer contradicts retrieved context.

**Model Response:**
{actual_output}

**Agent Trace (including Observations):**
{retrieval_context}

### Task
Check if the response contradicts ANY factual detail present in the retrieved context.

### Scoring
- **0** → No contradiction (consistent)
- **1** → Contradiction found (context inconsistency)

Return ONLY 0 or 1.
"""
    return metric

def build_logical_inconsistency_metric(model):
    """
    Detects invalid reasoning inside the model’s chain-of-thought.
    """

    metric = GEval(
        name="Logical_Inconsistency",
        criteria=(
            "Identify internal logical errors or contradictions between reasoning steps "
            "in the agent's trace and the final answer."
        ),
        evaluation_steps=[
            "Step 1: Identify reasoning steps in trace (Thought sections).",
            "Step 2: Check if reasoning logically leads to final answer.",
            "Step 3: Identify invalid arithmetic, contradictions, or unsupported conclusions.",
            "Step 4: Return score: 1 = inconsistency found, 0 = consistent."
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
- **0** → Reasoning is logically consistent.
- **1** → Logical inconsistency detected (math error, invalid inference, contradiction).

Return ONLY 0 or 1.
"""
    return metric




model = AzureOpenAIModel(
    model_name=AZURE_OPENAI_DEPLOYMENT_NAME,
    deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
    azure_openai_api_key=AZURE_OPENAI_API_KEY,
    openai_api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    temperature=0)

def is_bad_call(call):
    output = call["output"].lower()
    # A: empty / no results
    if "No more results" in output: return True
    if "page fetch failed" in output: return True
    if "No readable paragraphs" in output: return True
    # B: explicit error
    if "error" in output: return True
    if "404" in output: return True
    return False

def build_answer_given_metric(model):
    """
    Detects if the expected answer is present in the actual answer, accounting for
    different formats, punctuation, quotes, and word order variations.
    
    Example:
        Expected: "President Richard Nixon"
        Actual: "Matt Groening named the character Milhouse after the middle name of 
                President Richard Nixon, as he considered it to be an unfortunate name for a kid."
        Result: True (expected answer is semantically contained)
    """
    
    metric = GEval(
        name="Answer_Given",
        criteria=(
            "Determine if the expected answer is present in the actual answer, it is fine to include additional context or words as long as the expected answer is semantically contained in the actual answer. "
        ),
        evaluation_steps=[
            "Step 1: Extract the key entities and facts from the expected answer.",
            "Step 2: Check if the actual output contains these key entities/facts."
        ],
        model=model,
        evaluation_params=[
            LLMTestCaseParams.EXPECTED_OUTPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
    )
    
    metric.custom_prompt_template = """
You are an expert evaluator of answer matching.

**Expected Answer:**
{expected_output}

**Actual Output:**
{actual_output}

### Task
Determine if the expected answer (or its key entities and facts) is present in the actual output.
Account for different formats such as:
- Extra quotes or punctuation: "Richard Nixon" vs Richard Nixon
- Contractions vs full words: "don't" vs "do not"
- Abbreviations: "Pres." vs "President"
- Word order variations: "Richard Nixon" vs "Nixon, Richard"
- Extra context or words in between key terms

Return ONLY a number: 0 or 1
"""
    return metric

exact_match_metric = build_answer_given_metric(model=model)

def build_test_case(question: str, gold_answer: str, actual_answer: str, tool_calls, trace_text):
    """
    Convert a single HotpotQA run into a DeepEval LLMTestCase.
    """

    context_docs = [c["output"] for c in tool_calls]
    success_flag = gold_answer in actual_answer

    # 2. Tools called — REQUIRED for Execution Efficiency / Step Efficiency
    tools_called = [
        ToolCall(name=t["name"])
        for t in tool_calls
    ]

    return LLMTestCase(
        input=question,
        actual_output=actual_answer,
        expected_output=gold_answer,
        context=context_docs,
        retrieval_context=context_docs,

        # steps=steps,                # required by Step/Plan metrics
        tools_called=tools_called,  # <-- REQUIRED
        success=success_flag,
        additional_metadata={
            "trace": trace_text,
        },
    )

# DeepEval metrics
answer_relevancy_metric = AnswerRelevancyMetric(model=model)
faithfulness_metric = FaithfulnessMetric(model=model)
ctx_precision_metric = ContextualPrecisionMetric(model=model)
ctx_recall_metric = ContextualRecallMetric(model=model)
ctx_relevancy_metric = ContextualRelevancyMetric(model=model)
build_instruction_inconsistency_metric = build_instruction_inconsistency_metric(model=model)
build_context_inconsistency_metric = build_context_inconsistency_metric(model=model)
build_logical_inconsistency_metric = build_logical_inconsistency_metric(model=model)

def safe_measure(metric, test_case):
    """Run metric.measure safely and force success=True when missing."""
    metric.measure(test_case)

    # metrics like RAGAS set success=None → crash
    if getattr(metric, "success", None) is None:
        metric.success = True

    return metric



