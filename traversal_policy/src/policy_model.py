from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from common.config import TRAVERSAL_POLICY_PATH, TRAVERSAL_TOP_K
from knowledge_graph.src.retrieval_types import RetrievedMemoryBundle, RetrievedMemoryNode


@dataclass
class TraversalDecision:
    node_id: str | None
    action: str
    score: float


@dataclass
class TraversalPolicyCheckpoint:
    feature_weights: dict[str, float]
    bias: float = 0.0
    top_k: int = 3
    feature_means: dict[str, float] = field(default_factory=dict)
    feature_stds: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def extract_node_features(node: RetrievedMemoryNode) -> dict[str, float]:
    review_score = node.metadata.get("review_score")
    try:
        review_value = max(0.0, min(float(review_score) / 5.0, 1.0))
    except Exception:
        review_value = 0.0

    return {
        "base_total_score": float(node.metadata.get("base_total_score", node.total_score)),
        "current_total_score": float(node.total_score),
        "embedding_score": float(node.embedding_score or 0.0),
        "intent_score": float(node.intent_score or 0.0),
        "attribute_overlap_count": float(len(node.attribute_overlap)),
        "entity_overlap_count": float(len(node.entity_overlap)),
        "concept_match_count": float(len(node.ontology_matches or node.weak_concepts)),
        "weak_concept_count": float(len(node.weak_concepts)),
        "semantic_support_count": float(len(node.semantic_supports)),
        "review_score_norm": review_value,
        "is_experience": 1.0 if node.memory_type == "experience" else 0.0,
        "is_insight": 1.0 if node.memory_type == "insight" else 0.0,
        "is_observability_memory": 1.0 if node.memory_family == "observability" else 0.0,
        "is_semantic_memory": 1.0 if node.memory_family == "semantic" else 0.0,
        # Information-Theoretic Breakthrough Features (Q1 requirement)
        "marginal_gain": float(node.metadata.get("marginal_info_gain", 0.0)),
        "concept_variance": float(node.metadata.get("concept_assignment_variance", 0.0)),
        "ontology_alignment": float(max(node.metadata.get("node_assignment_scores", {"_": 0.0}).values())),
    }


class HeuristicTraversalPolicy:
    def __init__(self, top_k: int = TRAVERSAL_TOP_K):
        self.top_k = top_k

    def score_node(self, node: RetrievedMemoryNode) -> float:
        features = extract_node_features(node)
        return (
            features["current_total_score"]
            + (0.2 * features["review_score_norm"])
            + (0.1 * features["concept_match_count"])
            + (0.05 * features["is_experience"])
        )

    def rank_nodes(self, bundle: RetrievedMemoryBundle) -> list[tuple[RetrievedMemoryNode, float]]:
        scored = [(node, self.score_node(node)) for node in bundle.nodes]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored

    def select_nodes(self, bundle: RetrievedMemoryBundle) -> list[RetrievedMemoryNode]:
        remaining = list(bundle.nodes)
        selected: list[RetrievedMemoryNode] = []
        selected_types: set[str] = set()
        selected_concepts: set[str] = set()

        while remaining and len(selected) < self.top_k:
            best_node = None
            best_score = float("-inf")
            for node in remaining:
                features = extract_node_features(node)
                base_score = self.score_node(node)
                node_concepts = set(node.ontology_matches or node.weak_concepts)
                
                # Q1 Breakthrough: Dynamic Information-Theoretic Selection
                # Penalty for concept redundancy (sequential dependency)
                redundancy_count = len(node_concepts.intersection(selected_concepts))
                redundancy_penalty = 0.25 * redundancy_count
                
                # Bonus for uncertainty reduction and alignment
                info_bonus = (0.15 * features["marginal_gain"]) + (0.1 * features["ontology_alignment"])
                
                type_bonus = 0.15 if node.memory_type and node.memory_type not in selected_types else 0.0
                
                score = base_score + info_bonus + type_bonus - redundancy_penalty
                if score > best_score:
                    best_score = score
                    best_node = node

            if best_node is None:
                break

            selected.append(best_node)
            remaining = [node for node in remaining if node is not best_node]
            if best_node.memory_type:
                selected_types.add(best_node.memory_type)
            selected_concepts.update(best_node.ontology_matches or best_node.weak_concepts)

        return selected

    def decide(self, bundle: RetrievedMemoryBundle) -> list[TraversalDecision]:
        selected = [(node, self.score_node(node)) for node in self.select_nodes(bundle)]
        decisions = [
            TraversalDecision(node_id=node.node_id, action="select", score=score)
            for node, score in selected
        ]
        decisions.append(TraversalDecision(node_id=None, action="stop", score=0.0))
        return decisions


class WeightedTraversalPolicy(HeuristicTraversalPolicy):
    def __init__(self, checkpoint: TraversalPolicyCheckpoint):
        super().__init__(top_k=checkpoint.top_k)
        self.checkpoint = checkpoint

    def score_node(self, node: RetrievedMemoryNode) -> float:
        features = extract_node_features(node)
        score = float(self.checkpoint.bias)
        for name, value in features.items():
            numeric_value = float(value)
            std = float(self.checkpoint.feature_stds.get(name, 1.0) or 1.0)
            mean = float(self.checkpoint.feature_means.get(name, 0.0))
            normalized_value = (numeric_value - mean) / std if std > 0.0 else numeric_value
            score += float(self.checkpoint.feature_weights.get(name, 0.0)) * normalized_value
        return score

    @classmethod
    def from_file(cls, checkpoint_path: str | Path = TRAVERSAL_POLICY_PATH) -> "WeightedTraversalPolicy":
        checkpoint_path = Path(checkpoint_path)
        with checkpoint_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        checkpoint = TraversalPolicyCheckpoint(**payload)
        return cls(checkpoint)


def save_policy_checkpoint(checkpoint: TraversalPolicyCheckpoint, output_path: str | Path = TRAVERSAL_POLICY_PATH) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(checkpoint.to_dict(), handle, ensure_ascii=False, indent=2)
    return output_path
