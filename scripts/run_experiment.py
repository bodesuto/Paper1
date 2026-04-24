import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import DATA_PATH, TRAVERSAL_POLICY_PATH
from eval.test.react_test import test as react_test
from eval.test.react_test import test_dual_memory as react_test_dual_memory
from eval.test.reflexion_test import test as reflexion_test
from eval.test.reflexion_test import test_dual_memory as reflexion_test_dual_memory


def main():
    parser = argparse.ArgumentParser(description="Run DualMemoryKG experiments with explicit agent and retrieval strategy.")
    parser.add_argument("--agent", choices=["react", "reflexion"], required=True)
    parser.add_argument("--mode", choices=["baseline", "dual_memory"], required=True)
    parser.add_argument(
        "--strategy",
        choices=["heuristic", "vector_rag", "graph_rag", "ontology_only", "traversal_only", "learned", "full"],
        default=os.getenv("RETRIEVAL_STRATEGY", "heuristic"),
    )
    parser.add_argument("--data-path", default=os.path.join(DATA_PATH, "hard_bridge_500_validation.csv"))
    parser.add_argument("--output-path", required=True)
    args = parser.parse_args()

    if args.strategy == "full" and not Path(TRAVERSAL_POLICY_PATH).exists():
        raise FileNotFoundError(
            f"Traversal policy checkpoint not found at {TRAVERSAL_POLICY_PATH}. "
            "Run scripts/run_fit_traversal_policy.py before executing strategy=full."
        )

    if args.agent == "react" and args.mode == "baseline":
        react_test(args.data_path, args.output_path)
        return
    if args.agent == "react" and args.mode == "dual_memory":
        react_test_dual_memory(args.data_path, args.output_path, retrieval_strategy=args.strategy)
        return
    if args.agent == "reflexion" and args.mode == "baseline":
        reflexion_test(args.data_path, args.output_path)
        return
    if args.agent == "reflexion" and args.mode == "dual_memory":
        reflexion_test_dual_memory(args.data_path, args.output_path, retrieval_strategy=args.strategy)
        return

    raise ValueError("Unsupported experiment configuration")


if __name__ == "__main__":
    main()
