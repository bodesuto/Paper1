from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from domain_adapters.src.types import NormalizedCase


class DomainAdapter(ABC):
    domain_name: str = "unknown"

    @abstractmethod
    def adapt_records(self, records: list[dict[str, Any]]) -> list[NormalizedCase]:
        """
        Convert raw domain records into normalized cases.
        """

    def adapt_file(self, path: str | Path) -> list[NormalizedCase]:
        path = Path(path)
        if path.suffix.lower() == ".csv":
            return self.adapt_records(self._load_csv(path))
        return self.adapt_records(self._load_json(path))

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, Any]]:
        import pandas as pd

        return pd.read_csv(path).to_dict(orient="records")

    @staticmethod
    def _load_json(path: Path) -> list[dict[str, Any]]:
        import json

        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        raise ValueError(f"Unsupported JSON payload in {path}")
