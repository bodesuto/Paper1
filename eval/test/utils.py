from langchain.callbacks.base import BaseCallbackHandler
from neo4j import GraphDatabase

from common.config import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER
from common.env_setup import apply_env

def get_database_session():
    apply_env()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return driver.session()

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