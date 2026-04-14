from langchain_core.messages import HumanMessage
try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:
    from langchain.callbacks.base import BaseCallbackHandler

from common.models import get_llm, get_llm_with_trace
from common.logger import get_logger
from ..prompts.hotpot_prompts import reflection_prompt
from ..prompts.hotpot_examples import react_examples
from .react import creat_react_agent, format_examples, tool_calls

logger = get_logger(__name__)


class TraceHandler(BaseCallbackHandler):
    """Handler to capture trace output from ReAct agent execution."""
    def __init__(self):
        super().__init__()
        self.trace = ""

    def clear(self):
        self.trace = ""

    def on_llm_start(self, serialized, prompts, **kwargs):
        for prompt in prompts:
            self.trace = prompt

    def on_agent_action(self, action, **kwargs):
        self.trace += f"\nAction: {action.tool}\n"
        self.trace += f"Action Input: {action.tool_input}\n"

    def on_tool_end(self, output, **kwargs):
        self.trace += f"Observation: {output}\n"

    def on_agent_finish(self, finish, **kwargs):
        self.trace += f"\nFinal Answer: {finish.return_values.get('output', '')}\n"


def run_react_once(question: str, examples: None, agent, trace_handler):
    """Run the ReAct agent once and return (answer, trace).
    
    Args:
        question: The question to answer
        agent: The ReAct agent instance to use
    
    Returns:
        Tuple of (answer, trace)
    """
    # clear previous trace
    trace_handler.trace = ""
    # clear tool_calls as you already do
    tool_calls.clear()

    if examples is None:
        examples = react_examples
    examples = format_examples(examples)

    answer = agent.invoke({"input": question, "examples": examples})
    if isinstance(answer, dict):
        answer = answer.get("output", str(answer))
    trace = trace_handler.trace  # Assuming trace is set in agent's trace handler

    return answer, trace


def reflect_on_react_run(question: str, answer: str, trace: str, llm=None) -> str:
    """
    Returns a short reflection/instruction string to be fed into a second attempt.
    Uses a unified prompt (no system/human separation).
    """
    filled_prompt = reflection_prompt.format(
        question=question,
        answer=answer,
        trace=trace
    )
    if llm is None:
        llm = get_llm()

    resp = llm.invoke(
        [HumanMessage(content=filled_prompt)]
    )
    return resp.content


def reflexion_agent_run(question: str, examples, trace_handler=None, llm=None, agent=None):
    """
    Run ReAct once, reflect, then run a second ReAct attempt with reflection guidance.
    Returns (final_answer, debug_info_dict).
    
    Args:
        question: The question to answer.
        use_second_attempt_if_better: If True, use the second attempt. If False, use the first.
    
    Returns:
        Tuple of (final_answer, debug_info_dict) where debug_info_dict contains:
        - first_answer: Answer from first attempt
        - first_trace: Full trace from first attempt
        - reflection: Reflection on first attempt
        - second_answer: Answer from second attempt
        - second_trace: Full trace from second attempt
    """
    logger.info(f"Starting reflexion agent for question: {question}")
    if trace_handler is None:
        trace_handler = TraceHandler()

    if agent is None:
        agent = creat_react_agent(llm=get_llm_with_trace(trace_handler))

    if llm is None:
        llm = get_llm()
    
    # First attempt
    first_answer, first_trace = run_react_once(question, examples=examples, agent=agent, trace_handler=trace_handler)
    logger.info(f"First attempt answer: {first_answer}")
    reflection = reflect_on_react_run(question, first_answer, first_trace, llm=llm)
    logger.info(f"Reflection:\n{reflection}")

    # Build a modified question that includes the reflection as extra instruction
    reflected_question = (
        question
        + "\n\n[Reflection Guidance for Agent]\n"
        + reflection
        + "\n\n[End of Reflection Guidance]"
    )

    # Second attempt (with reflection-augmented question, same agent)
    second_answer, second_trace = run_react_once(reflected_question, examples=examples, agent=agent, trace_handler=trace_handler)
    logger.info(f"Second attempt answer: {second_answer}")

    debug_info = {
        "first_answer": first_answer,
        "first_trace": first_trace,
        "reflection": reflection,
        "second_answer": second_answer,
        "second_trace": second_trace,
    }

    logger.info(f"Final answer: {second_answer}")
    return second_answer, debug_info


__all__ = ["reflexion_agent_run", "run_react_once", "reflect_on_react_run", "trace_handler"]
