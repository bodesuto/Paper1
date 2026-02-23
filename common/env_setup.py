import os
from .config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
)

def apply_env():
    # Azure OpenAI (LangChain expects these)
    os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT
    os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY
    os.environ["AZURE_OPENAI_API_VERSION"] = AZURE_OPENAI_API_VERSION

    # Some libs still look for OpenAI-style vars
    os.environ.setdefault("OPENAI_API_TYPE", "azure")
    os.environ.setdefault("OPENAI_API_VERSION", AZURE_OPENAI_API_VERSION)
    os.environ.setdefault("OPENAI_API_KEY", AZURE_OPENAI_API_KEY)

