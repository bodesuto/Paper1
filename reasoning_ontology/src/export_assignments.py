from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from common.logger import get_logger
from reasoning_ontology.src.infer import OntologyInferenceEngine


logger = get_logger(__name__)


def export_ontology_assignments(
    input_records: list[dict[str, Any]],
    output_path: str | Path,
    text_key: str = "question",
) -> Path:
    engine = OntologyInferenceEngine()
    enriched = []
    for record in input_records:
        text = str(record.get(text_key, "")).strip()
        enriched.append(
            {
                **record,
                "ontology_assignments": engine.infer(text) if text else [],
            }
        )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(enriched, handle, ensure_ascii=False, indent=2)

    logger.info("Exported ontology assignments for %d records -> %s", len(enriched), output_path)
    return output_path
