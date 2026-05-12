import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import ALLOW_TRAIN_EVAL, DATA_PATH, TRAVERSAL_POLICY_PATH
from common.protocol import ensure_heldout_data_path
from eval.test.react_test import test as react_test
from eval.test.react_test import test_dual_memory as react_test_dual_memory
from eval.test.reflexion_test import test as reflexion_test
from eval.test.reflexion_test import test_dual_memory as reflexion_test_dual_memory


def run_test_safe(test_func, data_path, output_file, **kwargs):
    if Path(output_file).exists():
        print(f"Skipping {output_file} (already exists)")
        return
    print(f"\n>>> Running ablation: {output_file.name}")
    try:
        test_func(data_path, output_file, **kwargs)
    except Exception as e:
        print(f"FAILED ablation {output_file.name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run a compact ablation suite across baseline/heuristic/learned modes.")
    parser.add_argument("--agent", choices=["react", "reflexion"], default="react")
    parser.add_argument("--data-path", default=os.path.join(DATA_PATH, "hard_bridge_500_validation.csv"))
    parser.add_argument("--output-dir", default=os.path.join(DATA_PATH, "ablations"))
    parser.add_argument(
        "--allow-train-eval",
        action="store_true",
        default=ALLOW_TRAIN_EVAL,
        help="Explicitly allow running ablations on a train split. Disabled by default for academic rigor.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of rows to process.")
    args = parser.parse_args()

    ensure_heldout_data_path(args.data_path, allow_train_eval=args.allow_train_eval)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.agent == "react":
        run_test_safe(react_test_dual_memory, args.data_path, output_dir / "react_baseline.csv", retrieval_strategy="baseline", row_limit=args.limit)
        run_test_safe(react_test_dual_memory, args.data_path, output_dir / "react_heuristic.csv", retrieval_strategy="heuristic", row_limit=args.limit)
        run_test_safe(react_test_dual_memory, args.data_path, output_dir / "react_vector_rag.csv", retrieval_strategy="vector_rag", row_limit=args.limit)
        run_test_safe(react_test_dual_memory, args.data_path, output_dir / "react_graph_rag.csv", retrieval_strategy="graph_rag", row_limit=args.limit)
        run_test_safe(react_test_dual_memory, args.data_path, output_dir / "react_ontology_only.csv", retrieval_strategy="ontology_only", row_limit=args.limit)
        run_test_safe(react_test_dual_memory, args.data_path, output_dir / "react_traversal_only.csv", retrieval_strategy="traversal_only", row_limit=args.limit)
        run_test_safe(react_test_dual_memory, args.data_path, output_dir / "react_learned.csv", retrieval_strategy="learned", row_limit=args.limit)
        if Path(TRAVERSAL_POLICY_PATH).exists():
            run_test_safe(react_test_dual_memory, args.data_path, output_dir / "react_full.csv", retrieval_strategy="full", row_limit=args.limit)
        
        print("\n--- All ReAct ablations triggered. Waiting for cleanup... ---")
        import time
        time.sleep(5)
        return

    # Same for reflexion
    run_test_safe(reflexion_test_dual_memory, args.data_path, output_dir / "reflexion_baseline.csv", retrieval_strategy="baseline", row_limit=args.limit)
    run_test_safe(reflexion_test_dual_memory, args.data_path, output_dir / "reflexion_heuristic.csv", retrieval_strategy="heuristic", row_limit=args.limit)
    run_test_safe(reflexion_test_dual_memory, args.data_path, output_dir / "reflexion_vector_rag.csv", retrieval_strategy="vector_rag", row_limit=args.limit)
    run_test_safe(reflexion_test_dual_memory, args.data_path, output_dir / "reflexion_graph_rag.csv", retrieval_strategy="graph_rag", row_limit=args.limit)
    run_test_safe(reflexion_test_dual_memory, args.data_path, output_dir / "reflexion_ontology_only.csv", retrieval_strategy="ontology_only", row_limit=args.limit)
    run_test_safe(reflexion_test_dual_memory, args.data_path, output_dir / "reflexion_traversal_only.csv", retrieval_strategy="traversal_only", row_limit=args.limit)
    run_test_safe(reflexion_test_dual_memory, args.data_path, output_dir / "reflexion_learned.csv", retrieval_strategy="learned", row_limit=args.limit)
    if Path(TRAVERSAL_POLICY_PATH).exists():
        run_test_safe(reflexion_test_dual_memory, args.data_path, output_dir / "reflexion_full.csv", retrieval_strategy="full", row_limit=args.limit)

    print("\n--- All Reflexion ablations triggered. Waiting for cleanup... ---")
    import time
    time.sleep(5)


if __name__ == "__main__":
    main()
