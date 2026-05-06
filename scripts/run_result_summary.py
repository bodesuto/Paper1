import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import BOOTSTRAP_SAMPLES
from eval.test.result_summary import summarize_many


def main():
    parser = argparse.ArgumentParser(description="Summarize one or more result CSV files into a single table.")
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument(
        "--evidence-inputs",
        nargs="+",
        default=None,
        help="Optional annotated-evidence CSVs aligned one-to-one with --inputs.",
    )
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--reference", default=None, help="Optional baseline CSV for paired delta confidence intervals.")
    parser.add_argument("--bootstrap-samples", type=int, default=BOOTSTRAP_SAMPLES)
    args = parser.parse_args()

    summarize_many(
        args.inputs,
        output_path=args.output_path,
        bootstrap_samples=args.bootstrap_samples,
        reference_path=args.reference,
        evidence_csv_paths=args.evidence_inputs,
    )


if __name__ == "__main__":
    main()
