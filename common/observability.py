from __future__ import annotations

import atexit
from functools import lru_cache
from typing import Any

from common.logger import get_logger

from .config import (
    LANGFUSE_ENVIRONMENT,
    LANGFUSE_HOST,
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_RELEASE,
    LANGFUSE_SECRET_KEY,
    LANGFUSE_TRACING_ENABLED,
)
from .env_setup import apply_env


logger = get_logger(__name__)


def langfuse_is_enabled() -> bool:
    return bool(
        LANGFUSE_TRACING_ENABLED
        and LANGFUSE_PUBLIC_KEY
        and LANGFUSE_SECRET_KEY
        and LANGFUSE_HOST
    )


@lru_cache(maxsize=1)
def get_langfuse_client():
    if not langfuse_is_enabled():
        return None

    apply_env()
    try:
        from langfuse import Langfuse
    except Exception as exc:
        logger.warning("Langfuse SDK import failed; tracing disabled: %s", exc)
        return None

    try:
        return Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST,
            tracing_enabled=True,
            environment=LANGFUSE_ENVIRONMENT,
            release=LANGFUSE_RELEASE,
        )
    except Exception as exc:
        logger.warning("Failed to initialize Langfuse client; tracing disabled: %s", exc)
        return None


@lru_cache(maxsize=1)
def get_langfuse_callback_handler():
    client = get_langfuse_client()
    if client is None:
        return None

    try:
        from langfuse.langchain import CallbackHandler
    except Exception as exc:
        logger.warning("Langfuse LangChain callback unavailable; tracing disabled: %s", exc)
        return None

    try:
        return CallbackHandler(public_key=LANGFUSE_PUBLIC_KEY)
    except Exception as exc:
        logger.warning("Failed to initialize Langfuse LangChain callback; tracing disabled: %s", exc)
        return None


def build_callbacks(*callbacks: Any) -> list[Any]:
    built: list[Any] = []
    langfuse_handler = get_langfuse_callback_handler()
    if langfuse_handler is not None:
        built.append(langfuse_handler)
    for callback in callbacks:
        if callback is not None:
            built.append(callback)
    return built


def flush_observability() -> None:
    client = get_langfuse_client()
    if client is None:
        return
    try:
        client.flush()
    except Exception as exc:
        logger.debug("Langfuse flush skipped: %s", exc)


atexit.register(flush_observability)
