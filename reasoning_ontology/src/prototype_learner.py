from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from reasoning_ontology.src.dataset import OntologyTrainingExample
from reasoning_ontology.src.encoders import OntologyTextEncoder


@dataclass
class ConceptPrototype:
    prototype_id: str
    concept_type: str
    label: str
    count: int
    success_count: int = 0
    failure_count: int = 0
    centroid: list[float] = field(default_factory=list)
    positive_coherence: float = 0.0
    separation: float = 0.0
    prior_score: float = 0.0
    neighbor_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _dot(left: list[float], right: list[float]) -> float:
    return sum(float(a) * float(b) for a, b in zip(left, right))


def _l2_norm(vector: list[float]) -> float:
    return math.sqrt(sum(float(value) * float(value) for value in vector))


def _normalize(vector: list[float]) -> list[float]:
    if not vector:
        return []
    norm = _l2_norm(vector)
    if norm == 0.0:
        return [0.0 for _ in vector]
    return [float(value) / norm for value in vector]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return _dot(_normalize(left), _normalize(right))


def _weighted_average(vectors: list[list[float]], weights: list[float]) -> list[float]:
    if not vectors:
        return []
    dims = len(vectors[0])
    sums = [0.0] * dims
    total = 0.0
    for vector, weight in zip(vectors, weights):
        numeric_weight = max(float(weight), 0.0)
        total += numeric_weight
        for idx, value in enumerate(vector):
            sums[idx] += numeric_weight * float(value)
    if total <= 0.0:
        return [0.0] * dims
    return [value / total for value in sums]


def _blend_vectors(weighted_vectors: list[tuple[list[float], float]]) -> list[float]:
    vectors = [vector for vector, _ in weighted_vectors if vector]
    weights = [weight for vector, weight in weighted_vectors if vector]
    return _weighted_average(vectors, weights)


def _subtract(left: list[float], right: list[float], scale: float = 1.0) -> list[float]:
    if not left:
        return []
    if not right:
        return [float(value) for value in left]
    return [float(a) - (scale * float(b)) for a, b in zip(left, right)]


def _add(left: list[float], right: list[float], scale: float = 1.0) -> list[float]:
    if not left:
        return [scale * float(value) for value in right]
    if not right:
        return [float(value) for value in left]
    return [float(a) + (scale * float(b)) for a, b in zip(left, right)]


def _review_weight(example: OntologyTrainingExample) -> float:
    if example.review_score is None:
        return 1.0
    return max(0.6, min(float(example.review_score) / 4.0, 1.5))


def _example_weight(example: OntologyTrainingExample) -> float:
    status_weight = 1.35 if example.success else 0.85
    return status_weight * _review_weight(example)


def _concept_pairs(example: OntologyTrainingExample) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if example.weak_intent:
        pairs.append(("intent", example.weak_intent))
    pairs.extend(("attribute", value) for value in example.weak_attributes if value)
    pairs.extend(("entity", value) for value in example.weak_entities if value)
    return pairs


class WeakLabelPrototypeLearner:
    """
    Stronger ontology learner than the original mean-centroid baseline.

    It still starts from weak labels, but it now:
    - encodes all training texts once
    - upweights successful / high-review examples
    - smooths prototypes with same-type and co-occurring concept centroids
    - pushes prototypes away from same-type hard negatives
    - exposes coherence / separation / prior signals at inference time
    """

    def __init__(
        self,
        embeddings=None,
        *,
        type_smoothing: float = 0.20,
        neighbor_smoothing: float = 0.15,
        hard_negative_weight: float = 0.12,
    ):
        self.encoder = OntologyTextEncoder(embeddings=embeddings)
        self.prototypes: list[ConceptPrototype] = []
        self.type_smoothing = type_smoothing
        self.neighbor_smoothing = neighbor_smoothing
        self.hard_negative_weight = hard_negative_weight

    def fit(self, examples: list[OntologyTrainingExample]) -> list[ConceptPrototype]:
        if not examples:
            self.prototypes = []
            return self.prototypes

        texts = [example.text_for_encoding() for example in examples]
        embeddings = self.encoder.encode_many(texts)

        grouped_examples: dict[tuple[str, str], list[tuple[list[float], float, bool]]] = {}
        type_examples: dict[str, list[tuple[list[float], float]]] = {}
        prototype_neighbors: dict[str, dict[str, float]] = {}

        for example, embedding in zip(examples, embeddings):
            concepts = _concept_pairs(example)
            if not concepts:
                continue

            weight = _example_weight(example)
            for concept_type, label in concepts:
                grouped_examples.setdefault((concept_type, label), []).append((embedding, weight, bool(example.success)))
                type_examples.setdefault(concept_type, []).append((embedding, weight))

            prototype_ids = [f"{concept_type}::{label}" for concept_type, label in concepts]
            for left in prototype_ids:
                neighbors = prototype_neighbors.setdefault(left, {})
                for right in prototype_ids:
                    if left == right:
                        continue
                    neighbors[right] = neighbors.get(right, 0.0) + weight

        type_centroids = {
            concept_type: _blend_vectors(vectors)
            for concept_type, vectors in type_examples.items()
        }
        raw_centroids = {
            key: _blend_vectors([(embedding, weight) for embedding, weight, _ in vectors])
            for key, vectors in grouped_examples.items()
        }

        prototypes: list[ConceptPrototype] = []
        for (concept_type, label), vectors in sorted(grouped_examples.items()):
            prototype_id = f"{concept_type}::{label}"
            raw_centroid = raw_centroids[(concept_type, label)]
            type_centroid = type_centroids.get(concept_type, [])

            hard_negative_vectors: list[tuple[list[float], float]] = []
            for (other_type, other_label), other_vectors in grouped_examples.items():
                if other_type != concept_type or other_label == label:
                    continue
                hard_negative_vectors.extend((embedding, weight) for embedding, weight, _ in other_vectors)
            hard_negative_centroid = _blend_vectors(hard_negative_vectors)

            neighbor_vectors: list[tuple[list[float], float]] = []
            neighbor_ids: list[str] = []
            for neighbor_id, neighbor_weight in sorted(
                prototype_neighbors.get(prototype_id, {}).items(),
                key=lambda item: item[1],
                reverse=True,
            )[:4]:
                neighbor_type, neighbor_label = neighbor_id.split("::", 1)
                neighbor_centroid = raw_centroids.get((neighbor_type, neighbor_label))
                if neighbor_centroid:
                    neighbor_vectors.append((neighbor_centroid, neighbor_weight))
                    neighbor_ids.append(neighbor_id)
            neighbor_centroid = _blend_vectors(neighbor_vectors)

            centroid = list(raw_centroid)
            centroid = _add(centroid, type_centroid, self.type_smoothing)
            centroid = _add(centroid, neighbor_centroid, self.neighbor_smoothing)
            centroid = _subtract(centroid, hard_negative_centroid, self.hard_negative_weight)
            centroid = _normalize(centroid)

            success_count = sum(1 for _, _, success in vectors if success)
            failure_count = len(vectors) - success_count
            positive_coherence = (
                sum(_cosine_similarity(embedding, centroid) for embedding, _, _ in vectors) / len(vectors)
                if vectors
                else 0.0
            )
            separation = 1.0 - max(0.0, _cosine_similarity(centroid, hard_negative_centroid))
            success_rate = success_count / len(vectors) if vectors else 0.0
            prior_score = (
                0.45 * math.log1p(len(vectors))
                + 0.35 * success_rate
                + 0.20 * max(0.0, positive_coherence)
            )

            prototypes.append(
                ConceptPrototype(
                    prototype_id=prototype_id,
                    concept_type=concept_type,
                    label=label,
                    count=len(vectors),
                    success_count=success_count,
                    failure_count=failure_count,
                    centroid=centroid,
                    positive_coherence=positive_coherence,
                    separation=separation,
                    prior_score=prior_score,
                    neighbor_ids=neighbor_ids,
                )
            )

        self.prototypes = prototypes
        return self.prototypes

    def infer(self, text: str, top_k: int = 5) -> list[dict[str, Any]]:
        if not self.prototypes:
            return []

        text_embedding = self.encoder.encode(text)
        base_scores: list[dict[str, Any]] = []
        for prototype in self.prototypes:
            similarity = _cosine_similarity(text_embedding, prototype.centroid)
            support_bonus = min(math.log1p(prototype.count) / 6.0, 0.25)
            score = (
                similarity
                + (0.12 * prototype.prior_score)
                + (0.08 * prototype.positive_coherence)
                + (0.05 * prototype.separation)
                + support_bonus
            )
            base_scores.append(
                {
                    "prototype_id": prototype.prototype_id,
                    "concept_type": prototype.concept_type,
                    "label": prototype.label,
                    "score": score,
                    "similarity": similarity,
                    "support_count": prototype.count,
                    "success_rate": (
                        prototype.success_count / prototype.count if prototype.count else 0.0
                    ),
                    "coherence": prototype.positive_coherence,
                    "separation": prototype.separation,
                }
            )

        best_by_type: dict[str, list[float]] = {}
        for item in base_scores:
            best_by_type.setdefault(item["concept_type"], []).append(float(item["score"]))

        for item in base_scores:
            type_scores = sorted(best_by_type.get(item["concept_type"], []), reverse=True)
            current_score = float(item["score"])
            competitor = 0.0
            found_current = False
            for score in type_scores:
                if not found_current and abs(score - current_score) < 1e-9:
                    found_current = True
                    continue
                competitor = score
                break
            item["margin"] = item["score"] - competitor

        base_scores.sort(key=lambda item: (item["score"], item["margin"], item["support_count"]), reverse=True)
        return base_scores[:top_k]

    def save(self, output_path: str | Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump([prototype.to_dict() for prototype in self.prototypes], handle, ensure_ascii=False, indent=2)
        return output_path

    def load(self, input_path: str | Path) -> list[ConceptPrototype]:
        input_path = Path(input_path)
        with input_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        self.prototypes = [ConceptPrototype(**item) for item in data]
        return self.prototypes
