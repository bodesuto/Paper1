from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class NormalizedQuery:
    query_id: str
    domain: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NormalizedEvidenceUnit:
    evidence_id: str
    domain: str
    text: str
    evidence_type: str
    provenance: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NormalizedTrace:
    trace_id: str
    domain: str
    query_id: str
    trace_text: str
    success: bool | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NormalizedFailure:
    failure_id: str
    domain: str
    query_id: str
    root_cause: str | None = None
    explanation: str | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NormalizedInsight:
    insight_id: str
    domain: str
    query_id: str
    text: str
    provenance: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NormalizedCase:
    domain: str
    query: NormalizedQuery
    evidence_units: list[NormalizedEvidenceUnit] = field(default_factory=list)
    traces: list[NormalizedTrace] = field(default_factory=list)
    failures: list[NormalizedFailure] = field(default_factory=list)
    insights: list[NormalizedInsight] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "query": self.query.to_dict(),
            "evidence_units": [item.to_dict() for item in self.evidence_units],
            "traces": [item.to_dict() for item in self.traces],
            "failures": [item.to_dict() for item in self.failures],
            "insights": [item.to_dict() for item in self.insights],
            "metadata": self.metadata,
        }
