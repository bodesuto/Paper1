from __future__ import annotations

from pathlib import Path

from common.config import ALLOW_TRAIN_EVAL, REQUIRE_HELDOUT_EVAL


def infer_split_label(path: str | Path) -> str:
    stem = Path(path).stem.lower()
    tokens = stem.replace("-", "_").split("_")
    if "train" in tokens:
        return "train"
    if "test" in tokens:
        return "test"
    if "validation" in tokens or "val" in tokens or "dev" in tokens:
        return "validation"
    return "unknown"


def ensure_heldout_data_path(
    data_path: str | Path,
    *,
    require_heldout: bool = REQUIRE_HELDOUT_EVAL,
    allow_train_eval: bool = ALLOW_TRAIN_EVAL,
) -> str:
    split_label = infer_split_label(data_path)
    if require_heldout and split_label == "train" and not allow_train_eval:
        raise ValueError(
            f"Held-out evaluation protocol violation: {data_path} resolves to split=train. "
            "Use a validation/test file, or explicitly opt in with allow_train_eval."
        )
    return split_label
