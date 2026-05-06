import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

class AppSettings(BaseSettings):
    """Production-grade configuration management using Pydantic."""
    
    # API Keys
    GOOGLE_API_KEY: str = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", ""))
    GEMINI_MODEL_NAME: str = Field(default="gemini-2.5-flash")
    GEMINI_EMBEDDING_MODEL: str = Field(default="models/gemini-embedding-001")
    EMBEDDING_VECTOR_DIMENSIONS: int | None = Field(default=None)

    # Database
    NEO4J_URI: str = Field(default="")
    NEO4J_USER: str = Field(default="neo4j")
    NEO4J_PASSWORD: str = Field(default="")
    NEO4J_DATABASE: str = Field(default="neo4j")

    # Observability (Langfuse)
    LANGFUSE_HOST: str = Field(default="http://localhost:3000")
    LANGFUSE_PUBLIC_KEY: str = Field(default="")
    LANGFUSE_SECRET_KEY: str = Field(default="")
    LANGFUSE_TRACING_ENABLED: bool = Field(default=False)

    # Retrieval & Pipeline Paths
    RETRIEVAL_STRATEGY: str = Field(default="heuristic")
    OUTPUT_PATH: str = Field(default="./output/langfuse_export.json")
    DATA_PATH: str = Field(default="./eval/data")
    
    # Ontology Learner Params
    ONTOLOGY_TOP_K: int = Field(default=5)
    
    # Traversal Policy Params
    TRAVERSAL_TOP_K: int = Field(default=3)
    EVIDENCE_SELECTION_BUDGET: int = Field(default=3)
    
    # Testing & Evaluation
    BOOTSTRAP_SAMPLES: int = Field(default=1000)
    REQUIRE_HELDOUT_EVAL: bool = Field(default=True)
    ALLOW_TRAIN_EVAL: bool = Field(default=False)

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Instantiate the global config object
settings = AppSettings()

# Maintain backward compatibility for existing code during transition
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
GEMINI_MODEL_NAME = settings.GEMINI_MODEL_NAME
GEMINI_EMBEDDING_MODEL = settings.GEMINI_EMBEDDING_MODEL
EMBEDDING_VECTOR_DIMENSIONS = settings.EMBEDDING_VECTOR_DIMENSIONS
NEO4J_URI = settings.NEO4J_URI
NEO4J_USER = settings.NEO4J_USER
NEO4J_PASSWORD = settings.NEO4J_PASSWORD
NEO4J_DATABASE = settings.NEO4J_DATABASE
LANGFUSE_TRACING_ENABLED = settings.LANGFUSE_TRACING_ENABLED
OUTPUT_PATH = settings.OUTPUT_PATH
DATA_PATH = settings.DATA_PATH
RETRIEVAL_STRATEGY = settings.RETRIEVAL_STRATEGY
ONTOLOGY_TOP_K = settings.ONTOLOGY_TOP_K
TRAVERSAL_TOP_K = settings.TRAVERSAL_TOP_K
EVIDENCE_SELECTION_BUDGET = settings.EVIDENCE_SELECTION_BUDGET
BOOTSTRAP_SAMPLES = settings.BOOTSTRAP_SAMPLES
ALLOW_TRAIN_EVAL = settings.ALLOW_TRAIN_EVAL

# Optional dynamic paths
ONTOLOGY_PROTOTYPES_PATH = str(Path(OUTPUT_PATH).with_suffix(".ontology_prototypes.json"))
TRAVERSAL_POLICY_PATH = str(Path(OUTPUT_PATH).with_suffix(".traversal_policy.json"))
