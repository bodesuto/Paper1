import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import ALLOW_TRAIN_EVAL, DATA_PATH, TRAVERSAL_POLICY_PATH
from common.protocol import ensure_heldout_data_path
from eval.test.react_test import test_dual_memory as react_test_dual_memory
from eval.test.reflexion_test import test_dual_memory as reflexion_test_dual_memory
from eval.test.stress_tests import contradictory_insight, drop_memory_entries, inject_noisy_memory


def _noisy_transform(payload, row=None):
    question = (row or {}).get("question", "unknown question")
    noise = [f"Irrelevant memory about {question}", "Unrelated historical observation."]
    return inject_noisy_memory(payload, noise_texts=noise, max_noise=1)


def _missing_transform(payload, row=None):
    return drop_memory_entries(payload, keep_experiences=1, keep_insights=0)


def _contradiction_transform(payload, row=None):
    answer = (row or {}).get("answer", "unknown")
    return contradictory_insight(payload, contradiction=f"Contradictory insight: the answer is definitely not {answer}.")


TRANSFORMS = {
    "noisy": _noisy_transform,
    "missing": _missing_transform,
    "contradictory": _contradiction_transform,
}


def main():
    parser = argparse.ArgumentParser(description="Run robustness stress tests for memory-grounded evaluation.")
    parser.add_argument("--agent", choices=["react", "reflexion"], default="react")
    parser.add_argument("--strategy", choices=["heuristic", "ontology_only", "traversal_only", "learned", "full"], default="learned")
    parser.add_argument("--stress", choices=sorted(TRANSFORMS), required=True)
    parser.add_argument("--data-path", default=os.path.join(DATA_PATH, "hard_bridge_500_validation.csv"))
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--row-limit", type=int, default=20)
    parser.add_argument(
        "--allow-train-eval",
        action="store_true",
        default=ALLOW_TRAIN_EVAL,
        help="Explicitly allow running stress evaluation on a train split. Disabled by default for academic rigor.",
    )
    args = parser.parse_args()

    ensure_heldout_data_path(args.data_path, allow_train_eval=args.allow_train_eval)

    if args.strategy == "full" and not Path(TRAVERSAL_POLICY_PATH).exists():
        raise FileNotFoundError(
            f"Traversal policy checkpoint not found at {TRAVERSAL_POLICY_PATH}. "
            "Run scripts/run_fit_traversal_policy.py before executing stress tests with strategy=full."
        )

    test_fn = react_test_dual_memory if args.agent == "react" else reflexion_test_dual_memory
    test_fn(
        args.data_path,
        args.output_path,
        retrieval_strategy=args.strategy,
        memory_transform=TRANSFORMS[args.stress],
        row_limit=args.row_limit,
    )


if __name__ == "__main__":
    main()
