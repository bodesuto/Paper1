from __future__ import annotations

import json
import math
import random
from pathlib import Path

from common.config import TRAVERSAL_POLICY_PATH, TRAVERSAL_TOP_K
from traversal_policy.src.dataset import TraversalEpisode, TraversalStepRecord
from traversal_policy.src.policy_model import (
    TraversalPolicyCheckpoint,
    save_policy_checkpoint,
)


def _step_features(step: TraversalStepRecord) -> dict[str, float]:
    metadata = step.metadata or {}
    try:
        review_score = max(0.0, min(float(metadata.get("review_score", 0.0)) / 5.0, 1.0))
    except Exception:
        review_score = 0.0

    weak_concepts = metadata.get("weak_concepts", []) or []
    ontology_matches = metadata.get("ontology_matches", []) or []

    return {
        "base_total_score": float(metadata.get("base_total_score", step.score)),
        "current_total_score": float(step.score),
        "embedding_score": float(metadata.get("embedding_score", 0.0)),
        "intent_score": float(metadata.get("intent_score", 0.0)),
        "attribute_overlap_count": float(len(metadata.get("attribute_overlap", []))),
        "entity_overlap_count": float(len(metadata.get("entity_overlap", []))),
        "concept_match_count": float(len(ontology_matches or weak_concepts)),
        "weak_concept_count": float(len(weak_concepts)),
        "semantic_support_count": float(len(metadata.get("semantic_supports", []))),
        "review_score_norm": review_score,
        "is_experience": 1.0 if step.memory_type == "experience" else 0.0,
        "is_insight": 1.0 if step.memory_type == "insight" else 0.0,
        "is_observability_memory": 1.0 if metadata.get("memory_family") == "observability" else 0.0,
        "is_semantic_memory": 1.0 if metadata.get("memory_family") == "semantic" else 0.0,
    }


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _std(values: list[float], mean_value: float) -> float:
    if not values:
        return 1.0
    variance = sum((value - mean_value) ** 2 for value in values) / len(values)
    std = math.sqrt(max(variance, 0.0))
    return std if std > 1e-8 else 1.0


def _build_normalization_stats(
    feature_rows: list[dict[str, float]],
) -> tuple[list[str], dict[str, float], dict[str, float]]:
    feature_names = sorted({name for row in feature_rows for name in row})
    means: dict[str, float] = {}
    stds: dict[str, float] = {}
    for name in feature_names:
        values = [float(row.get(name, 0.0)) for row in feature_rows]
        mean_value = _mean(values)
        means[name] = mean_value
        stds[name] = _std(values, mean_value)
    return feature_names, means, stds


def _normalize_row(row: dict[str, float], means: dict[str, float], stds: dict[str, float]) -> dict[str, float]:
    normalized: dict[str, float] = {}
    for name in means:
        std = stds.get(name, 1.0) or 1.0
        normalized[name] = (float(row.get(name, 0.0)) - means[name]) / std
    return normalized


def _subtract_rows(left: dict[str, float], right: dict[str, float], feature_names: list[str]) -> list[float]:
    return [float(left.get(name, 0.0)) - float(right.get(name, 0.0)) for name in feature_names]


def _dot(left: list[float], right: list[float]) -> float:
    return sum(float(a) * float(b) for a, b in zip(left, right))


def load_policy_episodes(path: str | Path) -> list[TraversalEpisode]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    episodes: list[TraversalEpisode] = []
    for item in data:
        steps = [TraversalStepRecord(**step) for step in item.get("steps", [])]
        episodes.append(
            TraversalEpisode(
                question=item.get("question", ""),
                steps=steps,
                success=bool(item.get("success", False)),
            )
        )
    return episodes


def fit_weighted_policy(
    episodes: list[TraversalEpisode],
    top_k: int = TRAVERSAL_TOP_K,
    *,
    epochs: int = 16,
    learning_rate: float = 0.12,
    margin: float = 0.35,
    l2: float = 0.01,
    seed: int = 13,
) -> TraversalPolicyCheckpoint:
    feature_rows: list[dict[str, float]] = []
    selected_rows: list[dict[str, float]] = []
    unselected_rows: list[dict[str, float]] = []

    for episode in episodes:
        for step in episode.steps:
            features = _step_features(step)
            feature_rows.append(features)
            if step.selected and episode.success:
                selected_rows.append(features)
            else:
                unselected_rows.append(features)

    if not feature_rows:
        return TraversalPolicyCheckpoint(
            feature_weights={},
            bias=0.0,
            top_k=top_k,
            metadata={
                "episodes": 0,
                "training_method": "empty_dataset",
            },
        )

    feature_names, means, stds = _build_normalization_stats(feature_rows)

    pair_examples: list[tuple[list[float], float]] = []
    for episode in episodes:
        if not episode.steps:
            continue

        normalized_steps = [
            (step, _normalize_row(_step_features(step), means, stds))
            for step in episode.steps
        ]
        selected = [row for row in normalized_steps if row[0].selected]
        unselected = [row for row in normalized_steps if not row[0].selected]

        if episode.success:
            for selected_step, selected_features in selected:
                if not unselected:
                    continue
                for _, candidate_features in unselected:
                    pair_examples.append(
                        (_subtract_rows(selected_features, candidate_features, feature_names), 1.0)
                    )
        else:
            for failed_step, failed_features in selected:
                if not unselected:
                    continue
                for _, candidate_features in unselected:
                    pair_examples.append(
                        (_subtract_rows(failed_features, candidate_features, feature_names), -1.0)
                    )

    if not pair_examples:
        positive_mean = {
            name: _mean([_normalize_row(row, means, stds).get(name, 0.0) for row in selected_rows])
            for name in feature_names
        }
        negative_mean = {
            name: _mean([_normalize_row(row, means, stds).get(name, 0.0) for row in unselected_rows])
            for name in feature_names
        }
        feature_weights = {
            name: positive_mean.get(name, 0.0) - negative_mean.get(name, 0.0)
            for name in feature_names
        }
        return TraversalPolicyCheckpoint(
            feature_weights=feature_weights,
            bias=0.0,
            top_k=top_k,
            feature_means=means,
            feature_stds=stds,
            metadata={
                "episodes": len(episodes),
                "pair_examples": 0,
                "training_method": "mean_difference_fallback",
            },
        )

    rng = random.Random(seed)
    weights = [0.0 for _ in feature_names]
    averaged_weights = [0.0 for _ in feature_names]
    update_steps = 0

    for _ in range(max(1, epochs)):
        shuffled = list(pair_examples)
        rng.shuffle(shuffled)
        for feature_vector, label in shuffled:
            signed_margin = label * _dot(weights, feature_vector)
            if signed_margin < margin:
                for idx, value in enumerate(feature_vector):
                    gradient = (label * float(value)) - (l2 * weights[idx])
                    weights[idx] += learning_rate * gradient
            for idx, value in enumerate(weights):
                averaged_weights[idx] += value
            update_steps += 1

    if update_steps > 0:
        weights = [value / update_steps for value in averaged_weights]

    feature_weights = {
        name: weight
        for name, weight in zip(feature_names, weights)
    }

    return TraversalPolicyCheckpoint(
        feature_weights=feature_weights,
        bias=0.0,
        top_k=top_k,
        feature_means=means,
        feature_stds=stds,
        metadata={
            "episodes": len(episodes),
            "pair_examples": len(pair_examples),
            "training_method": "pairwise_margin_ranking",
            "epochs": epochs,
            "learning_rate": learning_rate,
            "margin": margin,
            "l2": l2,
        },
    )


def fit_and_save_policy(
    episode_path: str | Path,
    output_path: str | Path = TRAVERSAL_POLICY_PATH,
    top_k: int = TRAVERSAL_TOP_K,
) -> Path:
    episodes = load_policy_episodes(episode_path)
    checkpoint = fit_weighted_policy(episodes, top_k=top_k)
    return save_policy_checkpoint(checkpoint, output_path)
