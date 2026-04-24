from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:
    from langchain.callbacks.base import BaseCallbackHandler

from .config import GEMINI_MODEL_NAME, GEMINI_EMBEDDING_MODEL
from .env_setup import apply_env
from .observability import build_callbacks

def get_llm():
    apply_env()
    callbacks = build_callbacks()
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        temperature=0,
        callbacks=callbacks or None,
    )


def get_llm_with_trace(trace_handler: BaseCallbackHandler):
    """
    Get LLM with trace handler and callback manager.
    Returns tuple of (llm, trace_handler).
    """
    apply_env()
    callbacks = build_callbacks(trace_handler)

    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        temperature=0,
        callbacks=callbacks or None,
    )

    return llm


def get_embeddings():
    apply_env()
    return GoogleGenerativeAIEmbeddings(model=GEMINI_EMBEDDING_MODEL)
