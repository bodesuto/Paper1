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


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}

# Gemini
_google_api_key = os.getenv("GOOGLE_API_KEY")
_gemini_api_key = os.getenv("GEMINI_API_KEY")
GOOGLE_API_KEY = _google_api_key or _gemini_api_key
if not GOOGLE_API_KEY:
    raise ValueError("Missing required env var: set GOOGLE_API_KEY or GEMINI_API_KEY")
GEMINI_API_KEY = _gemini_api_key or GOOGLE_API_KEY
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "models/gemini-embedding-001",
)
_embedding_dims_raw = os.getenv("EMBEDDING_VECTOR_DIMENSIONS")
EMBEDDING_VECTOR_DIMENSIONS = int(_embedding_dims_raw) if _embedding_dims_raw else None

# Langfuse
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_TRACING_ENABLED = _bool_env("LANGFUSE_TRACING_ENABLED", default=False)
LANGFUSE_ENVIRONMENT = os.getenv("LANGFUSE_ENVIRONMENT")
LANGFUSE_RELEASE = os.getenv("LANGFUSE_RELEASE")
LANGFUSE_TRACE_NAME = os.getenv("LANGFUSE_TRACE_NAME")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "./output/langfuse_export.json")
DATA_PATH = os.getenv("DATA_PATH", "./eval/data")
CONFIDENT_API_KEY = os.getenv("CONFIDENT_API_KEY")
RETRIEVAL_STRATEGY = os.getenv("RETRIEVAL_STRATEGY", "heuristic")
# heuristic | vector_rag | graph_rag | ontology_only | traversal_only | learned | full
ALLOW_DEFAULT_EXAMPLE_PADDING = _bool_env("ALLOW_DEFAULT_EXAMPLE_PADDING", default=False)
ONTOLOGY_PROTOTYPES_PATH = os.getenv(
    "ONTOLOGY_PROTOTYPES_PATH",
    str(Path(OUTPUT_PATH).with_suffix(".ontology_prototypes.json")),
)
ONTOLOGY_SPLIT_MANIFEST_PATH = os.getenv(
    "ONTOLOGY_SPLIT_MANIFEST_PATH",
    str(Path(OUTPUT_PATH).with_suffix(".ontology_split_manifest.json")),
)
ONTOLOGY_TRAIN_SPLIT = os.getenv("ONTOLOGY_TRAIN_SPLIT", "train")
ONTOLOGY_TOP_K = int(os.getenv("ONTOLOGY_TOP_K", "5"))
LEARNED_RETRIEVAL_TOP_K = int(os.getenv("LEARNED_RETRIEVAL_TOP_K", "6"))
TRAVERSAL_POLICY_PATH = os.getenv(
    "TRAVERSAL_POLICY_PATH",
    str(Path(OUTPUT_PATH).with_suffix(".traversal_policy.json")),
)
TRAVERSAL_SPLIT_MANIFEST_PATH = os.getenv(
    "TRAVERSAL_SPLIT_MANIFEST_PATH",
    str(Path(OUTPUT_PATH).with_suffix(".traversal_split_manifest.json")),
)
TRAVERSAL_TRAIN_SPLIT = os.getenv("TRAVERSAL_TRAIN_SPLIT", "train")
TRAVERSAL_TOP_K = int(os.getenv("TRAVERSAL_TOP_K", "3"))
DATASET_SPLIT_SEED = int(os.getenv("DATASET_SPLIT_SEED", "13"))
EVIDENCE_SELECTION_BUDGET = int(os.getenv("EVIDENCE_SELECTION_BUDGET", str(TRAVERSAL_TOP_K)))
EVIDENCE_FRONTIER_MULTIPLIER = int(os.getenv("EVIDENCE_FRONTIER_MULTIPLIER", "4"))
EVIDENCE_QUERY_CONCEPT_WEIGHT = float(os.getenv("EVIDENCE_QUERY_CONCEPT_WEIGHT", "1.0"))
EVIDENCE_SUPPORT_WEIGHT = float(os.getenv("EVIDENCE_SUPPORT_WEIGHT", "0.35"))
EVIDENCE_FAMILY_BONUS = float(os.getenv("EVIDENCE_FAMILY_BONUS", "0.20"))
EVIDENCE_REDUNDANCY_PENALTY = float(os.getenv("EVIDENCE_REDUNDANCY_PENALTY", "0.15"))
EVIDENCE_COST_PENALTY = float(os.getenv("EVIDENCE_COST_PENALTY", "0.05"))
BOOTSTRAP_SAMPLES = int(os.getenv("BOOTSTRAP_SAMPLES", "1000"))

# Neo4j
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

