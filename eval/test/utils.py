from contextlib import contextmanager

try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:
    from langchain.callbacks.base import BaseCallbackHandler
from neo4j import GraphDatabase

from common.config import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER
from common.env_setup import apply_env

@contextmanager
def get_database_session():
    apply_env()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    session = driver.session(database=NEO4J_DATABASE) if NEO4J_DATABASE else driver.session()
    try:
        yield session
    finally:
        session.close()
        driver.close()


class DummyUsageCallback:
    def __init__(self):
        self.prompt_tokens = None
        self.completion_tokens = None
        self.total_tokens = None
        self.successful_requests = None
        self.total_cost = None


@contextmanager
def get_usage_callback():
    # Gemini does not expose OpenAI callback accounting through LangChain's
    # get_openai_callback API, so we provide a no-op tracker to keep eval flows alive.
    yield DummyUsageCallback()

class FullReActTrace(BaseCallbackHandler):
    def __init__(self):
        self.trace = ""

    # # Capture the LLM prompt before generation
    def on_llm_start(self, serialized, prompts, **kwargs):
        for p in prompts:
            self.trace = p

    # ReAct actions
    def on_agent_action(self, action, **kwargs):
        self.trace += f"\nAction: {action.tool}\n"
        self.trace += f"Action Input: {action.tool_input}\n"

    # Tool results
    def on_tool_end(self, output, **kwargs):
        self.trace += f"Observation: {output}\n"

    # Final answer
    def on_agent_finish(self, finish, **kwargs):
        self.trace += f"\nFinal Answer: {finish.return_values.get('output', '')}\n"
