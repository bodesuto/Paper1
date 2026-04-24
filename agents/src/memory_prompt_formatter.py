from __future__ import annotations


def _stringify_items(items) -> list[str]:
    if items is None:
        return []
    if isinstance(items, str):
        return [items.strip()] if items.strip() else []
    if isinstance(items, dict):
        return [f"{key}: {value}" for key, value in items.items()]
    if isinstance(items, (list, tuple)):
        cleaned = []
        for item in items:
            text = str(item).strip()
            if text:
                cleaned.append(text)
        return cleaned
    text = str(items).strip()
    return [text] if text else []


def format_memory_payload(payload) -> str:
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, (list, tuple)):
        return "\n\n".join(_stringify_items(payload))
    if not isinstance(payload, dict):
        return str(payload)

    sections: list[str] = []

    experiences = _stringify_items(payload.get("experiences"))
    insights = _stringify_items(payload.get("insights"))
    ontology_concepts = _stringify_items(payload.get("ontology_concepts"))
    selected_path = _stringify_items(payload.get("selected_path"))
    grounding_metadata = _stringify_items(payload.get("grounding_metadata"))
    semantic_supports = _stringify_items(payload.get("semantic_supports"))

    if experiences:
        sections.append("Successful past traces:\n" + "\n\n".join(experiences))
    if insights:
        sections.append("Failure insights:\n" + "\n".join(f"- {item}" for item in insights))
    if ontology_concepts:
        sections.append("Relevant ontology concepts:\n" + "\n".join(f"- {item}" for item in ontology_concepts))
    if selected_path:
        sections.append("Selected memory path:\n" + "\n".join(f"- {item}" for item in selected_path))
    if semantic_supports:
        sections.append("Semantic support evidence:\n" + "\n".join(f"- {item}" for item in semantic_supports))
    if grounding_metadata:
        sections.append("Grounding metadata:\n" + "\n".join(f"- {item}" for item in grounding_metadata))

    return "\n\n".join(section for section in sections if section.strip())
