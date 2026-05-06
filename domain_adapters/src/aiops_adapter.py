from __future__ import annotations

from typing import Any

from domain_adapters.src.base import DomainAdapter
from domain_adapters.src.types import (
    NormalizedCase,
    NormalizedFailure,
    NormalizedInsight,
    NormalizedQuery,
    NormalizedTrace,
)


class AIOpsAdapter(DomainAdapter):
    domain_name = "aiops"

    def adapt_records(self, records: list[dict[str, Any]]) -> list[NormalizedCase]:
        cases: list[NormalizedCase] = []
        for idx, record in enumerate(records):
            query_id = str(record.get("id") or record.get("memory_key") or idx)
            question = str(
                record.get("question")
                or record.get("incident")
                or record.get("problem")
                or record.get("title")
                or ""
            ).strip()
            if not question:
                continue

            query = NormalizedQuery(
                query_id=query_id,
                domain=self.domain_name,
                text=question,
                metadata={
                    "service": record.get("service"),
                    "severity": record.get("severity"),
                    "status": record.get("status"),
                },
            )

            traces: list[NormalizedTrace] = []
            trace_text = str(record.get("trace", "")).strip()
            if trace_text:
                traces.append(
                    NormalizedTrace(
                        trace_id=f"{query_id}:trace:0",
                        domain=self.domain_name,
                        query_id=query_id,
                        trace_text=trace_text,
                        success=bool(record.get("success", record.get("status"))),
                        provenance={"source_record_id": query_id},
                    )
                )

            failures: list[NormalizedFailure] = []
            root_cause = record.get("root_cause")
            explanation = record.get("explanation")
            if root_cause or explanation:
                failures.append(
                    NormalizedFailure(
                        failure_id=f"{query_id}:failure:0",
                        domain=self.domain_name,
                        query_id=query_id,
                        root_cause=str(root_cause).strip() if root_cause else None,
                        explanation=str(explanation).strip() if explanation else None,
                        provenance={"source_record_id": query_id},
                    )
                )

            insights: list[NormalizedInsight] = []
            insight_text = str(record.get("insights", "")).strip()
            if insight_text:
                insights.append(
                    NormalizedInsight(
                        insight_id=f"{query_id}:insight:0",
                        domain=self.domain_name,
                        query_id=query_id,
                        text=insight_text,
                        provenance={"source_record_id": query_id},
                    )
                )

            cases.append(
                NormalizedCase(
                    domain=self.domain_name,
                    query=query,
                    traces=traces,
                    failures=failures,
                    insights=insights,
                    metadata={"adapter": "aiops"},
                )
            )
        return cases
