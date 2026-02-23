import os
from dotenv import load_dotenv

def _req(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise ValueError(f"Missing required env var: {name}")
    return v


load_dotenv()
# Azure
AZURE_OPENAI_ENDPOINT = _req("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = _req("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")

# LangSmith
LANGSMITH_PROJECT = _req("LANGSMITH_PROJECT")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", f"./output/langsmith_runs_{LANGSMITH_PROJECT}.json")
DATA_PATH = os.getenv("DATA_PATH", "./eval/data")
CONFIDENT_API_KEY = _req("CONFIDENT_API_KEY")

# Neo4j
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

