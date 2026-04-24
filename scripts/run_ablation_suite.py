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
    parser = argparse.ArgumentParser(description="Run a compact ablation suite across baseline/heuristic/learned modes.")
    parser.add_argument("--agent", choices=["react", "reflexion"], default="react")
    parser.add_argument("--data-path", default=os.path.join(DATA_PATH, "hard_bridge_500_validation.csv"))
    parser.add_argument("--output-dir", default=os.path.join(DATA_PATH, "ablations"))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.agent == "react":
        react_test(args.data_path, output_dir / "react_baseline.csv")
        react_test_dual_memory(args.data_path, output_dir / "react_heuristic.csv", retrieval_strategy="heuristic")
        react_test_dual_memory(args.data_path, output_dir / "react_vector_rag.csv", retrieval_strategy="vector_rag")
        react_test_dual_memory(args.data_path, output_dir / "react_graph_rag.csv", retrieval_strategy="graph_rag")
        react_test_dual_memory(args.data_path, output_dir / "react_ontology_only.csv", retrieval_strategy="ontology_only")
        react_test_dual_memory(args.data_path, output_dir / "react_traversal_only.csv", retrieval_strategy="traversal_only")
        react_test_dual_memory(args.data_path, output_dir / "react_learned.csv", retrieval_strategy="learned")
        if Path(TRAVERSAL_POLICY_PATH).exists():
            react_test_dual_memory(args.data_path, output_dir / "react_full.csv", retrieval_strategy="full")
        return

    reflexion_test(args.data_path, output_dir / "reflexion_baseline.csv")
    reflexion_test_dual_memory(args.data_path, output_dir / "reflexion_heuristic.csv", retrieval_strategy="heuristic")
    reflexion_test_dual_memory(args.data_path, output_dir / "reflexion_vector_rag.csv", retrieval_strategy="vector_rag")
    reflexion_test_dual_memory(args.data_path, output_dir / "reflexion_graph_rag.csv", retrieval_strategy="graph_rag")
    reflexion_test_dual_memory(args.data_path, output_dir / "reflexion_ontology_only.csv", retrieval_strategy="ontology_only")
    reflexion_test_dual_memory(args.data_path, output_dir / "reflexion_traversal_only.csv", retrieval_strategy="traversal_only")
    reflexion_test_dual_memory(args.data_path, output_dir / "reflexion_learned.csv", retrieval_strategy="learned")
    if Path(TRAVERSAL_POLICY_PATH).exists():
        reflexion_test_dual_memory(args.data_path, output_dir / "reflexion_full.csv", retrieval_strategy="full")


if __name__ == "__main__":
    main()
