from __future__ import annotations

from dataclasses import dataclass
import re

from common.config import (
    EVIDENCE_COST_PENALTY,
    EVIDENCE_FAMILY_BONUS,
    EVIDENCE_QUERY_CONCEPT_WEIGHT,
    EVIDENCE_REDUNDANCY_PENALTY,
    EVIDENCE_SUPPORT_WEIGHT,
)
from knowledge_graph.src.retrieval_types import RetrievedMemoryBundle, RetrievedMemoryNode


TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")
STOPWORDS = {
    "the",
    "a",
    "an",
    "of",
    "and",
    "or",
    "to",
    "in",
    "is",
    "was",
    "for",
    "on",
    "with",
}


def _tokenize(text: str) -> set[str]:
    tokens = {token.lower() for token in TOKEN_RE.findall(text or "")}
    return {token for token in tokens if token not in STOPWORDS and len(token) > 1}


@dataclass
class EvidenceSelectionConfig:
    query_concept_weight: float = EVIDENCE_QUERY_CONCEPT_WEIGHT
    support_weight: float = EVIDENCE_SUPPORT_WEIGHT
    family_bonus: float = EVIDENCE_FAMILY_BONUS
    redundancy_penalty: float = EVIDENCE_REDUNDANCY_PENALTY
    cost_penalty: float = EVIDENCE_COST_PENALTY


def query_concepts(bundle: RetrievedMemoryBundle) -> set[str]:
    return {
        str(concept).strip()
        for concept in bundle.metadata.get("query_concepts", [])
        if str(concept).strip()
    }


def node_concepts(node: RetrievedMemoryNode) -> set[str]:
    concepts = node.learned_concepts or node.ontology_matches or node.weak_concepts
    return {str(concept).strip() for concept in concepts if str(concept).strip()}


def node_support_units(node: RetrievedMemoryNode) -> set[str]:
    units: set[str] = set()
    for support in node.semantic_supports:
        units.update(_tokenize(str(support)))
    preview = node.prompt_text()
    if preview:
        units.update(_tokenize(preview) - {"question", "answer"})
    return units


def node_cost(node: RetrievedMemoryNode) -> float:
    score = max(float(node.total_score), 1e-6)
    support_cost = min(len(node.semantic_supports), 3) * 0.03
    memory_cost = 0.05 if node.memory_type == "insight" else 0.0
    return (1.0 / score) + support_cost + memory_cost


def marginal_gain(
    *,
    bundle: RetrievedMemoryBundle,
    node: RetrievedMemoryNode,
    selected_nodes: list[RetrievedMemoryNode],
    selected_concepts: set[str],
    selected_support_units: set[str],
    selected_families: set[str],
    config: EvidenceSelectionConfig,
    base_score: float = 0.0,
) -> tuple[float, dict[str, float]]:
    q_concepts = query_concepts(bundle)
    n_concepts = node_concepts(node)
    support_units = node_support_units(node)

    new_query_concepts = n_concepts.intersection(q_concepts).difference(selected_concepts)
    new_support = support_units.difference(selected_support_units)
    redundancy = 0.0
    for prev in selected_nodes:
        prev_concepts = node_concepts(prev)
        union = n_concepts.union(prev_concepts)
        if union:
            redundancy += len(n_concepts.intersection(prev_concepts)) / len(union)

    family_gain = 1.0 if node.memory_family and node.memory_family not in selected_families else 0.0
    concept_gain = config.query_concept_weight * float(len(new_query_concepts))
    support_gain = config.support_weight * float(len(new_support))
    diversity_gain = config.family_bonus * family_gain
    redundancy_cost = config.redundancy_penalty * redundancy
    selection_cost = config.cost_penalty * node_cost(node)
    total_gain = base_score + concept_gain + support_gain + diversity_gain - redundancy_cost - selection_cost

    return total_gain, {
        "base_score": base_score,
        "concept_gain": concept_gain,
        "support_gain": support_gain,
        "diversity_gain": diversity_gain,
        "redundancy_cost": redundancy_cost,
        "selection_cost": selection_cost,
        "new_query_concepts": float(len(new_query_concepts)),
        "new_support_units": float(len(new_support)),
    }
