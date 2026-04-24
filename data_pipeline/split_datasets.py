from __future__ import annotations

import json
import hashlib
import random
from pathlib import Path
from typing import Any


def _stable_group_key(record: dict[str, Any], key_fields: tuple[str, ...]) -> str:
    raw_parts: list[str] = []
    for field in key_fields:
        raw_parts.append(str(record.get(field, "")).strip())
    joined = "||".join(raw_parts).strip()
    if joined:
        return joined
    fallback = json.dumps(record, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(fallback.encode("utf-8")).hexdigest()


def build_group_split_manifest(
    records: list[dict[str, Any]],
    *,
    key_fields: tuple[str, ...] = ("question",),
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    seed: int = 42,
) -> dict[str, Any]:
    grouped: dict[str, list[int]] = {}
    for idx, record in enumerate(records):
        grouped.setdefault(_stable_group_key(record, key_fields), []).append(idx)

    group_keys = list(grouped)
    rng = random.Random(seed)
    rng.shuffle(group_keys)

    train_end = int(len(group_keys) * train_ratio)
    val_end = train_end + int(len(group_keys) * val_ratio)
    assignments: dict[str, str] = {}
    for group_key in group_keys[:train_end]:
        assignments[group_key] = "train"
    for group_key in group_keys[train_end:val_end]:
        assignments[group_key] = "val"
    for group_key in group_keys[val_end:]:
        assignments[group_key] = "test"

    split_counts = {"train": 0, "val": 0, "test": 0}
    for group_key, indices in grouped.items():
        split_counts[assignments[group_key]] += len(indices)

    return {
        "seed": seed,
        "key_fields": list(key_fields),
        "group_count": len(group_keys),
        "record_count": len(records),
        "group_assignments": assignments,
        "split_counts": split_counts,
    }


def split_records_with_manifest(
    records: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    key_fields = tuple(str(field) for field in manifest.get("key_fields", ["question"]))
    assignments = dict(manifest.get("group_assignments", {}))
    splits: dict[str, list[dict[str, Any]]] = {"train": [], "val": [], "test": []}
    for record in records:
        split = assignments.get(_stable_group_key(record, key_fields), "test")
        splits.setdefault(split, []).append(record)
    return splits


def save_grouped_splits(
    records: list[dict[str, Any]],
    *,
    output_base_path: str | Path,
    manifest_path: str | Path,
    key_fields: tuple[str, ...] = ("question",),
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    seed: int = 42,
) -> dict[str, Path]:
    output_base_path = Path(output_base_path)
    manifest_path = Path(manifest_path)
    output_base_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = build_group_split_manifest(
        records,
        key_fields=key_fields,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        seed=seed,
    )
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)

    split_records = split_records_with_manifest(records, manifest)
    outputs: dict[str, Path] = {}
    for split_name, split_payload in split_records.items():
        split_path = output_base_path.with_suffix(f".{split_name}.json")
        with split_path.open("w", encoding="utf-8") as handle:
            json.dump(split_payload, handle, ensure_ascii=False, indent=2)
        outputs[split_name] = split_path
    outputs["manifest"] = manifest_path
    return outputs


def split_json_records(
    input_path: str | Path,
    output_dir: str | Path,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    seed: int = 42,
) -> dict[str, Path]:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8") as handle:
        records: list[dict[str, Any]] = json.load(handle)

    rng = random.Random(seed)
    rng.shuffle(records)

    train_end = int(len(records) * train_ratio)
    val_end = train_end + int(len(records) * val_ratio)

    splits = {
        "train": records[:train_end],
        "val": records[train_end:val_end],
        "test": records[val_end:],
    }

    output_paths: dict[str, Path] = {}
    for split_name, split_records in splits.items():
        path = output_dir / f"{input_path.stem}.{split_name}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(split_records, handle, ensure_ascii=False, indent=2)
        output_paths[split_name] = path

    return output_paths
