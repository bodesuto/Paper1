import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from eval.test.annotated_evidence import score_against_annotations


def main():
    parser = argparse.ArgumentParser(description="Score retrieval paths against manually annotated evidence.")
    parser.add_argument("--results-csv", required=True)
    parser.add_argument("--annotations-path", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--summary-path", required=True)
    args = parser.parse_args()

    _, summary = score_against_annotations(
        args.results_csv,
        args.annotations_path,
        output_path=args.output_path,
        summary_path=args.summary_path,
    )
    print(summary)


if __name__ == "__main__":
    main()
