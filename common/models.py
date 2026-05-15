import os
from functools import lru_cache

try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:
    from langchain.callbacks.base import BaseCallbackHandler

from .config import (
    MODEL_PROVIDER,
    MODEL_NAME,
    GEMINI_EMBEDDING_MODEL,
    GOOGLE_API_KEY,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    GROQ_API_KEY,
    MISTRAL_API_KEY,
    TOGETHER_API_KEY,
    OLLAMA_BASE_URL,
)
from .env_setup import apply_env
from .observability import build_callbacks


def _instantiate_llm(provider: str, model: str, callbacks=None):
    """Factory helper to instantiate LLM based on provider."""
    provider = provider.lower()
    
    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=model, temperature=0, callbacks=callbacks)
    
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, api_key=OPENAI_API_KEY, temperature=0, callbacks=callbacks)
    
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model, api_key=ANTHROPIC_API_KEY, temperature=0, callbacks=callbacks)
        
    elif provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=model, groq_api_key=GROQ_API_KEY, temperature=0, callbacks=callbacks)
        
    elif provider == "mistral":
        from langchain_mistralai import ChatMistralAI
        return ChatMistralAI(model=model, api_key=MISTRAL_API_KEY, temperature=0, callbacks=callbacks)
        
    elif provider == "together":
        # Together AI is often used via LangChain's OpenAIChat compatible or dedicated Together integration
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model, 
            openai_api_key=TOGETHER_API_KEY, 
            openai_api_base="https://api.together.xyz/v1",
            temperature=0, 
            callbacks=callbacks
        )
    
    elif provider == "ollama":
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(model=model, base_url=OLLAMA_BASE_URL, temperature=0, callbacks=callbacks)
    
    else:
        raise ValueError(f"Unsupported MODEL_PROVIDER: {provider}. Choose from: google, openai, anthropic, ollama, groq, mistral, together")


@lru_cache(maxsize=1)
def get_llm():
    apply_env()
    callbacks = build_callbacks()
    return _instantiate_llm(MODEL_PROVIDER, MODEL_NAME, callbacks=callbacks or None)


def get_llm_with_trace(trace_handler: BaseCallbackHandler):
    """Get LLM with specific trace handler (used in ReAct/Reflexion loops)."""
    apply_env()
    callbacks = build_callbacks(trace_handler)
    return _instantiate_llm(MODEL_PROVIDER, MODEL_NAME, callbacks=callbacks or None)


@lru_cache(maxsize=1)
def get_embeddings():
    apply_env()
    # Embeddings stay on Gemini to ensure vector space consistency for existing Neo4j/Chroma records.
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    return GoogleGenerativeAIEmbeddings(model=GEMINI_EMBEDDING_MODEL)
