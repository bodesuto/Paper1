import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import BOOTSTRAP_SAMPLES, DATA_PATH
from experiments.theorem_suite import run_theorem_aligned_suite


def main():
    parser = argparse.ArgumentParser(description="Run the theorem-aligned paper experiment suite.")
    parser.add_argument("--agent", choices=["react", "reflexion"], default="react")
    parser.add_argument("--data-path", default=str(Path(DATA_PATH) / "hard_bridge_500_validation.csv"))
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--annotations-path", default=None)
    parser.add_argument("--bootstrap-samples", type=int, default=BOOTSTRAP_SAMPLES)
    args = parser.parse_args()

    run_theorem_aligned_suite(
        repo_root=Path(__file__).resolve().parent.parent,
        agent=args.agent,
        data_path=args.data_path,
        output_dir=args.output_dir,
        annotations_path=args.annotations_path,
        bootstrap_samples=args.bootstrap_samples,
    )


if __name__ == "__main__":
    main()
