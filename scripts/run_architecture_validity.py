import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.architecture_validity import build_architecture_validity_report


def main():
    parser = argparse.ArgumentParser(description="Build an architecture-validity and error-decomposition report for paper analysis.")
    parser.add_argument("--summary-csv", required=True)
    parser.add_argument("--results-csv", default=None)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--error-output-path", default=None)
    args = parser.parse_args()

    report, _ = build_architecture_validity_report(
        args.summary_csv,
        results_csv=args.results_csv,
        output_path=args.output_path,
        error_output_path=args.error_output_path,
    )
    print(report)


if __name__ == "__main__":
    main()
