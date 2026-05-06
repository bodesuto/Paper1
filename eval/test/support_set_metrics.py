from __future__ import annotations


def set_jaccard(left: set[str], right: set[str]) -> float:
    union = left.union(right)
    if not union:
        return 1.0
    return len(left.intersection(right)) / len(union)


def support_set_best_match(
    predicted: set[str],
    sufficient_sets: list[set[str]],
) -> dict[str, float]:
    if not sufficient_sets:
        return {
            "support_set_best_precision": 0.0,
            "support_set_best_recall": 0.0,
            "support_set_best_f1": 0.0,
            "support_set_best_jaccard": 0.0,
            "support_set_exact_match": 0.0,
        }

    best = {
        "support_set_best_precision": 0.0,
        "support_set_best_recall": 0.0,
        "support_set_best_f1": 0.0,
        "support_set_best_jaccard": 0.0,
        "support_set_exact_match": 0.0,
    }

    for support_set in sufficient_sets:
        if not support_set and not predicted:
            precision = recall = f1 = jaccard = 1.0
            exact_match = 1.0
        else:
            overlap = len(predicted.intersection(support_set))
            precision = overlap / len(predicted) if predicted else 0.0
            recall = overlap / len(support_set) if support_set else 0.0
            f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
            jaccard = set_jaccard(predicted, support_set)
            exact_match = 1.0 if predicted == support_set else 0.0

        candidate = {
            "support_set_best_precision": precision,
            "support_set_best_recall": recall,
            "support_set_best_f1": f1,
            "support_set_best_jaccard": jaccard,
            "support_set_exact_match": exact_match,
        }
        if (
            candidate["support_set_best_f1"],
            candidate["support_set_exact_match"],
            candidate["support_set_best_jaccard"],
        ) > (
            best["support_set_best_f1"],
            best["support_set_exact_match"],
            best["support_set_best_jaccard"],
        ):
            best = candidate

    return best
