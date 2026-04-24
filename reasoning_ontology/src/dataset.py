from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class OntologyTrainingExample:
    example_id: str
    question: str
    trace: str
    success: bool
    source: str
    review_score: float | None = None
    root_cause: str | None = None
    explanation: str | None = None
    insights: str | None = None
    weak_intent: str | None = None
    weak_attributes: list[str] = field(default_factory=list)
    weak_entities: list[str] = field(default_factory=list)

    def text_for_encoding(self) -> str:
        parts = [self.question.strip()]
        if self.trace:
            parts.append(self.trace.strip())
        if self.explanation:
            parts.append(self.explanation.strip())
        if self.insights:
            parts.append(str(self.insights).strip())
        return "\n\n".join(part for part in parts if part)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if isinstance(value, tuple):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def _load_json(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"Expected list in {path}")
    return data


def _entry_to_example(entry: dict[str, Any], source: str) -> OntologyTrainingExample | None:
    question = entry.get("question")
    trace = entry.get("trace")
    if not question or not trace:
        return None

    vocab = entry.get("vocab") or {}
    rca = entry.get("rca") or {}
    review_score = entry.get("review_score")
    try:
        numeric_review = float(review_score) if review_score is not None else None
    except Exception:
        numeric_review = None

    success = entry.get("success", entry.get("status"))
    if success is None:
        success = numeric_review is not None and numeric_review > 3.0

    return OntologyTrainingExample(
        example_id=str(entry.get("memory_key") or entry.get("id") or question).strip(),
        question=str(question),
        trace=str(trace),
        success=bool(success),
        source=source,
        review_score=numeric_review,
        root_cause=rca.get("root_cause") or entry.get("root_cause"),
        explanation=rca.get("explanation") or entry.get("explanation"),
        insights=rca.get("insights") or entry.get("insights"),
        weak_intent=vocab.get("intent"),
        weak_attributes=_coerce_list(vocab.get("attributes")),
        weak_entities=_coerce_list(vocab.get("entities")),
    )


def build_ontology_dataset(
    hil_classified_path: str | Path,
    rca_classified_path: str | Path | None = None,
) -> list[OntologyTrainingExample]:
    examples: list[OntologyTrainingExample] = []

    for entry in _load_json(hil_classified_path):
        example = _entry_to_example(entry, source="hil")
        if example is not None:
            examples.append(example)

    if rca_classified_path is not None:
        for entry in _load_json(rca_classified_path):
            example = _entry_to_example(entry, source="rca")
            if example is not None:
                examples.append(example)

    return examples


def save_ontology_dataset(examples: list[OntologyTrainingExample], output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump([example.to_dict() for example in examples], handle, ensure_ascii=False, indent=2)
    return output_path
