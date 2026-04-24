from __future__ import annotations

import random
from copy import deepcopy
from typing import Any


def inject_noisy_memory(memory_payload: dict[str, Any], noise_texts: list[str], max_noise: int = 1, seed: int = 42) -> dict[str, Any]:
    rng = random.Random(seed)
    payload = deepcopy(memory_payload)
    experiences = list(payload.get("experiences", []))
    rng.shuffle(noise_texts)
    experiences.extend(noise_texts[:max_noise])
    payload["experiences"] = experiences
    return payload


def drop_memory_entries(memory_payload: dict[str, Any], keep_experiences: int = 1, keep_insights: int = 1) -> dict[str, Any]:
    payload = deepcopy(memory_payload)
    payload["experiences"] = list(payload.get("experiences", []))[:keep_experiences]
    payload["insights"] = list(payload.get("insights", []))[:keep_insights]
    return payload


def contradictory_insight(memory_payload: dict[str, Any], contradiction: str) -> dict[str, Any]:
    payload = deepcopy(memory_payload)
    payload.setdefault("insights", [])
    payload["insights"] = list(payload["insights"]) + [contradiction]
    return payload
