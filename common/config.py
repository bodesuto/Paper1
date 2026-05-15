import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

class AppSettings(BaseSettings):
    """Production-grade configuration management using Pydantic."""
    
    # API Keys & Provider Config
    MODEL_PROVIDER: str = Field(default="google")  # choices: google, openai, anthropic, ollama, groq, mistral, together
    GOOGLE_API_KEY: str = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", ""))
    OPENAI_API_KEY: str = Field(default="")
    ANTHROPIC_API_KEY: str = Field(default="")
    GROQ_API_KEY: str = Field(default="")
    MISTRAL_API_KEY: str = Field(default="")
    TOGETHER_API_KEY: str = Field(default="")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")

    # Model Names
    MODEL_NAME: str = Field(default="gemini-2.5-flash") # Override with gpt-4o, claude-3-5-sonnet, etc.
    GEMINI_MODEL_NAME: str = Field(default="gemini-2.5-flash") # Fallback for backward compatibility
    GEMINI_EMBEDDING_MODEL: str = Field(default="models/gemini-embedding-001")
    EMBEDDING_VECTOR_DIMENSIONS: int | None = Field(default=None)

    @field_validator("EMBEDDING_VECTOR_DIMENSIONS", mode="before")
    @classmethod
    def parse_empty_int(cls, v: Any) -> Any:
        if v == "":
            return None
        return v

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
    LANGFUSE_ENVIRONMENT: str = Field(default="")
    LANGFUSE_RELEASE: str = Field(default="")

    @field_validator("LANGFUSE_TRACING_ENABLED", mode="before")
    @classmethod
    def parse_bool(cls, v: Any) -> Any:
        if isinstance(v, str):
            if v.lower() in ("true", "1", "yes"):
                return True
            if v.lower() in ("false", "0", "no", ""):
                return False
        return v

    # Retrieval & Pipeline Paths
    RETRIEVAL_STRATEGY: str = Field(default="heuristic")
    OUTPUT_PATH: str = Field(default="./output/langfuse_export.json")
    DATA_PATH: str = Field(default="./eval/data")
    
    # Ontology Learner Params
    ONTOLOGY_TOP_K: int = Field(default=5)
    LEARNED_RETRIEVAL_TOP_K: int = Field(default=6)
    
    # Traversal Policy Params
    TRAVERSAL_TOP_K: int = Field(default=3)
    EVIDENCE_SELECTION_BUDGET: int = Field(default=3)
    
    # Testing & Evaluation
    BOOTSTRAP_SAMPLES: int = Field(default=1000)
    REQUIRE_HELDOUT_EVAL: bool = Field(default=True)
    ALLOW_TRAIN_EVAL: bool = Field(default=False)

    # Retrieval & Evidence Selection Tuning
    ALLOW_DEFAULT_EXAMPLE_PADDING: bool = Field(default=True)
    EVIDENCE_QUERY_CONCEPT_WEIGHT: float = Field(default=0.8)
    EVIDENCE_SUPPORT_WEIGHT: float = Field(default=0.6)
    EVIDENCE_FAMILY_BONUS: float = Field(default=0.3)
    EVIDENCE_REDUNDANCY_PENALTY: float = Field(default=0.4)
    EVIDENCE_COST_PENALTY: float = Field(default=0.1)
    EVIDENCE_FRONTIER_MULTIPLIER: int = Field(default=2)

    @field_validator("ALLOW_DEFAULT_EXAMPLE_PADDING", mode="before")
    @classmethod
    def parse_bool_padding(cls, v: Any) -> Any:
        return cls.parse_bool(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Important: ignore extra fields from .env
        case_sensitive=False
    )

# Instantiate the global config object
settings = AppSettings()

# Maintain backward compatibility for existing code during transition
MODEL_PROVIDER = settings.MODEL_PROVIDER
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
GEMINI_API_KEY = settings.GOOGLE_API_KEY  # Alias
OPENAI_API_KEY = settings.OPENAI_API_KEY
ANTHROPIC_API_KEY = settings.ANTHROPIC_API_KEY
GROQ_API_KEY = settings.GROQ_API_KEY
MISTRAL_API_KEY = settings.MISTRAL_API_KEY
TOGETHER_API_KEY = settings.TOGETHER_API_KEY
OLLAMA_BASE_URL = settings.OLLAMA_BASE_URL

MODEL_NAME = settings.MODEL_NAME
GEMINI_MODEL_NAME = settings.GEMINI_MODEL_NAME
GEMINI_EMBEDDING_MODEL = settings.GEMINI_EMBEDDING_MODEL
EMBEDDING_VECTOR_DIMENSIONS = settings.EMBEDDING_VECTOR_DIMENSIONS
NEO4J_URI = settings.NEO4J_URI
NEO4J_USER = settings.NEO4J_USER
NEO4J_PASSWORD = settings.NEO4J_PASSWORD
NEO4J_DATABASE = settings.NEO4J_DATABASE

LANGFUSE_HOST = settings.LANGFUSE_HOST
LANGFUSE_PUBLIC_KEY = settings.LANGFUSE_PUBLIC_KEY
LANGFUSE_SECRET_KEY = settings.LANGFUSE_SECRET_KEY
LANGFUSE_TRACING_ENABLED = settings.LANGFUSE_TRACING_ENABLED
LANGFUSE_ENVIRONMENT = settings.LANGFUSE_ENVIRONMENT
LANGFUSE_RELEASE = settings.LANGFUSE_RELEASE
OUTPUT_PATH = settings.OUTPUT_PATH
DATA_PATH = settings.DATA_PATH
RETRIEVAL_STRATEGY = settings.RETRIEVAL_STRATEGY
ONTOLOGY_TOP_K = settings.ONTOLOGY_TOP_K
LEARNED_RETRIEVAL_TOP_K = settings.LEARNED_RETRIEVAL_TOP_K
TRAVERSAL_TOP_K = settings.TRAVERSAL_TOP_K
EVIDENCE_SELECTION_BUDGET = settings.EVIDENCE_SELECTION_BUDGET
BOOTSTRAP_SAMPLES = settings.BOOTSTRAP_SAMPLES
REQUIRE_HELDOUT_EVAL = settings.REQUIRE_HELDOUT_EVAL
ALLOW_TRAIN_EVAL = settings.ALLOW_TRAIN_EVAL

ALLOW_DEFAULT_EXAMPLE_PADDING = settings.ALLOW_DEFAULT_EXAMPLE_PADDING
EVIDENCE_QUERY_CONCEPT_WEIGHT = settings.EVIDENCE_QUERY_CONCEPT_WEIGHT
EVIDENCE_SUPPORT_WEIGHT = settings.EVIDENCE_SUPPORT_WEIGHT
EVIDENCE_FAMILY_BONUS = settings.EVIDENCE_FAMILY_BONUS
EVIDENCE_REDUNDANCY_PENALTY = settings.EVIDENCE_REDUNDANCY_PENALTY
EVIDENCE_COST_PENALTY = settings.EVIDENCE_COST_PENALTY
EVIDENCE_FRONTIER_MULTIPLIER = settings.EVIDENCE_FRONTIER_MULTIPLIER

# Optional dynamic paths
ONTOLOGY_PROTOTYPES_PATH = str(Path(OUTPUT_PATH).with_suffix(".ontology_prototypes.json"))
TRAVERSAL_POLICY_PATH = str(Path(OUTPUT_PATH).with_suffix(".traversal_policy.json"))
