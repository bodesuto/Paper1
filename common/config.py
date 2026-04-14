import os
from pathlib import Path
from dotenv import load_dotenv

def _req(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise ValueError(f"Missing required env var: {name}")
    return v

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Gemini
GOOGLE_API_KEY = _req("GOOGLE_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "models/gemini-embedding-001",
)

# LangSmith
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "default")
LANGSMITH_PROJECT_ID = os.getenv("LANGSMITH_PROJECT_ID")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", f"./output/langsmith_runs_{LANGSMITH_PROJECT}.json")
DATA_PATH = os.getenv("DATA_PATH", "./eval/data")
CONFIDENT_API_KEY = os.getenv("CONFIDENT_API_KEY")

# Neo4j
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

