from __future__ import annotations

import json
import re
from typing import Any


TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")
STOPWORDS = {
    "the",
    "a",
    "an",
    "of",
    "and",
    "or",
    "to",
    "in",
    "is",
    "was",
    "for",
    "on",
    "with",
    "who",
    "what",
    "when",
    "where",
    "which",
}


def _tokenize(text: str) -> set[str]:
    tokens = {token.lower() for token in TOKEN_RE.findall(text or "")}
    return {token for token in tokens if token not in STOPWORDS and len(token) > 1}


def _ensure_json(value: Any, default):
    if value is None:
        return default
    if isinstance(value, (list, dict)):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
        try:
            return json.loads(value)
        except Exception:
            return default
    return default


def lexical_support_ratio(answer: str, support_texts: list[str]) -> float:
    answer_tokens = _tokenize(answer)
    if not answer_tokens:
        return 0.0
    support_tokens = set()
    for text in support_texts:
        support_tokens.update(_tokenize(text))
    if not support_tokens:
        return 0.0
    return len(answer_tokens.intersection(support_tokens)) / len(answer_tokens)


def unsupported_reasoning_score(answer: str, support_texts: list[str], threshold: float = 0.2) -> float:
    return 1.0 if lexical_support_ratio(answer, support_texts) < threshold else 0.0


def path_grounding_precision(answer: str, retrieval_path: Any) -> float:
    path_items = _ensure_json(retrieval_path, [])
    if not path_items:
        return 0.0
    answer_tokens = _tokenize(answer)
    if not answer_tokens:
        return 0.0

    grounded = 0
    for item in path_items:
        preview = str((item or {}).get("text_preview", ""))
        concept_tokens = _tokenize(" ".join((item or {}).get("ontology_matches", []) + (item or {}).get("weak_concepts", [])))
        preview_tokens = _tokenize(preview)
        if answer_tokens.intersection(preview_tokens.union(concept_tokens)):
            grounded += 1
    return grounded / len(path_items)


def memory_selection_accuracy(retrieval_path: Any, memory_payload: Any) -> float:
    path_items = _ensure_json(retrieval_path, [])
    payload = _ensure_json(memory_payload, {})
    if not path_items:
        return 0.0

    expected_concepts = set(_ensure_json(payload.get("ontology_concepts"), []) if isinstance(payload, dict) else [])
    selected = 0
    for item in path_items:
        item = item or {}
        has_supportive_type = item.get("memory_type") in {"experience", "insight"}
        matched = bool(set(item.get("ontology_matches", [])).intersection(expected_concepts)) if expected_concepts else bool(item.get("weak_concepts"))
        if has_supportive_type and matched:
            selected += 1
    return selected / len(path_items)


def evidence_sufficiency_rate(answer: str, memory_payload: Any, tool_calls: list[dict[str, Any]] | None = None, threshold: float = 0.2) -> float:
    payload = _ensure_json(memory_payload, {})
    support_texts: list[str] = []
    if isinstance(payload, dict):
        support_texts.extend(str(item) for item in payload.get("experiences", []))
        support_texts.extend(str(item) for item in payload.get("insights", []))
    for call in tool_calls or []:
        output = call.get("output")
        if output:
            support_texts.append(str(output))
    return 1.0 if lexical_support_ratio(answer, support_texts) >= threshold else 0.0


def summarize_grounding_metrics(
    question: str,
    answer: str,
    retrieval_path: Any,
    memory_payload: Any,
    tool_calls: list[dict[str, Any]] | None = None,
) -> dict[str, float]:
    payload = _ensure_json(memory_payload, {})
    support_texts: list[str] = []
    if isinstance(payload, dict):
        support_texts.extend(str(item) for item in payload.get("experiences", []))
        support_texts.extend(str(item) for item in payload.get("insights", []))
    for call in tool_calls or []:
        output = call.get("output")
        if output:
            support_texts.append(str(output))

    return {
        "lexical_support_ratio": lexical_support_ratio(answer, support_texts),
        "unsupported_reasoning_score": unsupported_reasoning_score(answer, support_texts),
        "path_grounding_precision": path_grounding_precision(answer, retrieval_path),
        "memory_selection_accuracy": memory_selection_accuracy(retrieval_path, memory_payload),
        "evidence_sufficiency_rate": evidence_sufficiency_rate(answer, memory_payload, tool_calls=tool_calls),
    }
