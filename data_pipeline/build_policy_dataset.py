from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from traversal_policy.src.dataset import TraversalEpisode, episode_from_retrieval_log


def _parse_json_field(value: Any, default):
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


def build_policy_dataset_from_retrieval_logs(
    retrieval_log_path: str | Path,
    output_path: str | Path,
) -> tuple[Path, list[dict[str, Any]]]:
    retrieval_log_path = Path(retrieval_log_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if retrieval_log_path.suffix.lower() == ".csv":
        df = pd.read_csv(retrieval_log_path)
        records: list[dict[str, Any]] = []
        for row in df.to_dict(orient="records"):
            traversal = _parse_json_field(row.get("traversal"), {})
            memory_payload = _parse_json_field(row.get("memory_payload"), {})
            candidate_retrieval_path = _parse_json_field(row.get("candidate_retrieval_path"), [])
            selected_retrieval_path = _parse_json_field(row.get("retrieval_path"), [])
            records.append(
                {
                    "question": row.get("question"),
                    "exact_match": row.get("exact_match"),
                    "exact_match_eval": row.get("exact_match_eval"),
                    "path_grounding_precision": row.get("path_grounding_precision"),
                    "evidence_sufficiency_rate": row.get("evidence_sufficiency_rate"),
                    "unsupported_reasoning_score": row.get("unsupported_reasoning_score"),
                    "contradiction_exposure_rate": row.get("contradiction_exposure_rate"),
                    "selected_node_ids": traversal.get("selected_node_ids", memory_payload.get("selected_node_ids", [])),
                    "retrieval_path": candidate_retrieval_path or selected_retrieval_path,
                    "selected_retrieval_path": selected_retrieval_path,
                }
            )
    else:
        with retrieval_log_path.open("r", encoding="utf-8") as handle:
            records = json.load(handle)

    episodes: list[dict[str, Any]] = []
    for record in records:
        episode: TraversalEpisode = episode_from_retrieval_log(record)
        episodes.append(episode.to_dict())

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(episodes, handle, ensure_ascii=False, indent=2)

    return output_path, episodes
