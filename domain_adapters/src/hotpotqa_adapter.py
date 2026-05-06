from __future__ import annotations

import ast
from typing import Any

from domain_adapters.src.base import DomainAdapter
from domain_adapters.src.types import NormalizedCase, NormalizedEvidenceUnit, NormalizedQuery


def _parse_context_field(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        parsed = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = ast.literal_eval(text)
        except Exception:
            return [text]
    else:
        return [str(value)]

    evidence_texts: list[str] = []
    if isinstance(parsed, dict):
        for sentences in parsed.get("sentences", []):
            if isinstance(sentences, list):
                evidence_texts.extend(str(sentence).strip() for sentence in sentences if str(sentence).strip())
        return evidence_texts

    for item in parsed:
        if isinstance(item, list):
            evidence_texts.extend(str(entry).strip() for entry in item if str(entry).strip())
        elif isinstance(item, str) and item.strip():
            evidence_texts.append(item.strip())
    return evidence_texts


class HotpotQAAdapter(DomainAdapter):
    domain_name = "hotpotqa"

    def adapt_records(self, records: list[dict[str, Any]]) -> list[NormalizedCase]:
        cases: list[NormalizedCase] = []
        for idx, record in enumerate(records):
            query_id = str(record.get("id", idx))
            question = str(record.get("question", "")).strip()
            if not question:
                continue

            query = NormalizedQuery(
                query_id=query_id,
                domain=self.domain_name,
                text=question,
                metadata={
                    "gold_answer": record.get("answer"),
                    "type": record.get("type"),
                    "level": record.get("level"),
                },
            )

            evidence_units: list[NormalizedEvidenceUnit] = []
            evidence_texts = _parse_context_field(record.get("context"))
            for evidence_idx, text in enumerate(evidence_texts):
                evidence_units.append(
                    NormalizedEvidenceUnit(
                        evidence_id=f"{query_id}:ctx:{evidence_idx}",
                        domain=self.domain_name,
                        text=text,
                        evidence_type="support_passage",
                        provenance={
                            "source_record_id": query_id,
                            "source_field": "context",
                        },
                    )
                )

            cases.append(
                NormalizedCase(
                    domain=self.domain_name,
                    query=query,
                    evidence_units=evidence_units,
                    metadata={
                        "dataset": "hotpotqa_style",
                        "supporting_facts": record.get("supporting_facts"),
                    },
                )
            )
        return cases
