from __future__ import annotations

from pathlib import Path
from typing import Any

from common.config import ONTOLOGY_PROTOTYPES_PATH, ONTOLOGY_TOP_K
from common.logger import get_logger
from reasoning_ontology.src.prototype_learner import WeakLabelPrototypeLearner


logger = get_logger(__name__)


class OntologyInferenceEngine:
    def __init__(self, prototype_path: str | Path | None = None, top_k: int | None = None):
        self.prototype_path = Path(prototype_path or ONTOLOGY_PROTOTYPES_PATH)
        self.top_k = top_k or ONTOLOGY_TOP_K
        self.learner = WeakLabelPrototypeLearner()
        self.loaded = False

    def ensure_loaded(self) -> bool:
        if self.loaded:
            return True
        if not self.prototype_path.exists():
            logger.warning("Ontology prototypes not found at %s", self.prototype_path)
            return False
        self.learner.load(self.prototype_path)
        self.loaded = True
        return True

    def infer(self, text: str, top_k: int | None = None) -> list[dict[str, Any]]:
        if not self.ensure_loaded():
            return []
        return self.learner.infer(text, top_k=top_k or self.top_k)

    def concept_keys(self, text: str, top_k: int | None = None) -> list[str]:
        assignments = self.infer(text, top_k=max(top_k or self.top_k, self.top_k))
        selected: list[str] = []
        seen_types: set[str] = set()

        for item in assignments:
            concept_type = str(item.get("concept_type", "")).strip()
            prototype_id = str(item.get("prototype_id", "")).strip()
            if not prototype_id:
                continue
            if concept_type and concept_type in seen_types and float(item.get("margin", 0.0)) < 0.03:
                continue
            selected.append(prototype_id)
            if concept_type:
                seen_types.add(concept_type)
            if len(selected) >= (top_k or self.top_k):
                break

        if selected:
            return selected
        return [item["prototype_id"] for item in assignments[: top_k or self.top_k]]
