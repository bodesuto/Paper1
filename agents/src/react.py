from langchain.tools import tool
try:
    from langchain_classic.agents import initialize_agent, AgentType
except ImportError:
    from langchain.agents import initialize_agent, AgentType
from langchain_core.callbacks import CallbackManager
from langchain_core.prompts import PromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper

from common.models import get_llm
from common.logger import get_logger
from common.observability import build_callbacks
from ..prompts.hotpot_prompts import react_prompt
from .memory_prompt_formatter import format_memory_payload


import threading

logger = get_logger(__name__)

# Use thread-local storage for tool calls to ensure thread safety in production
_thread_local = threading.local()

def _get_tool_calls_buffer():
    if not hasattr(_thread_local, "tool_calls"):
        _thread_local.tool_calls = []
    return _thread_local.tool_calls

def clear_tool_calls():
    _thread_local.tool_calls = []

def get_tool_calls():
    return list(_get_tool_calls_buffer())



wiki_api = WikipediaAPIWrapper(
    top_k_results=2,              # get top 2 pages
    lang="en",                    # English Wikipedia
    doc_content_chars_max=2000    # limit to 2000 chars per doc
)

# Removed global tool_calls for thread safety


def format_examples(examples) -> str:
    """Normalize examples/memory payloads into a prompt-friendly string."""
    return format_memory_payload(examples)


@tool("search_wikipedia", return_direct=False)
def search_wikipedia(entity: str) -> str:
    """Search Wikipedia for an entity or topic and return a short preview."""
    try:
        result = wiki_api.run(entity)
        if not result:
            result = f"No Wikipedia information found for {entity}."
    except Exception as e:
        result = f"Search error for '{entity}': {e}"

    _get_tool_calls_buffer().append(
        {
            "name": "search_wikipedia",
            "input": {"entity": entity},
            "output": result,
        }
    )
    return result



@tool("lookup_keyword", return_direct=False)
def lookup_keyword(keyword: str) -> str:
    """Look up a keyword or phrase in Wikipedia and return a brief contextual summary."""
    try:
        result = wiki_api.run(keyword)
        if not result:
            result = f"No relevant Wikipedia data found for '{keyword}'."
    except Exception as e:
        result = f"Lookup error for '{keyword}': {e}"

    _get_tool_calls_buffer().append(
        {
            "name": "lookup_keyword",
            "input": {"keyword": keyword},
            "output": result,
        }
    )
    return result


def create_react_agent(prompt: str = react_prompt, llm=None):
    """
    Create and return a ReAct agent.
    
    Args:
        prompt: The prompt template string with {examples} and {input} placeholders
        input: The question/input for the agent (optional at initialization, can be passed at runtime)
        prompt_examples: The few-shot examples to inject into {examples} placeholder (str or list)
        llm: The language model to use. If None, will call get_llm()
    
    Returns:
        An initialized agent ready to run with .run() or .invoke()
    """
    if llm is None:
        llm = get_llm()
    
    tools = [search_wikipedia, lookup_keyword]
    
    prompt_template = PromptTemplate(
        input_variables=["input", "examples"], 
        template=prompt
    )
    callbacks = build_callbacks()
    callback_manager = CallbackManager(handlers=callbacks) if callbacks else None

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        callback_manager=callback_manager,
        prompt=prompt_template,
        handle_parsing_errors=True,
        max_iterations=8,
    )
    return agent


__all__ = ["create_react_agent", "search_wikipedia", "lookup_keyword", "get_tool_calls", "clear_tool_calls", "format_examples"]
