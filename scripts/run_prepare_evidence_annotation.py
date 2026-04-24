import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from eval.test.annotated_evidence import build_annotation_template


def main():
    parser = argparse.ArgumentParser(description="Create an annotation template for evidence-grounding review.")
    parser.add_argument("--results-csv", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    path = build_annotation_template(args.results_csv, args.output_path, limit=args.limit)
    print(f"Saved evidence annotation template: {path}")


if __name__ == "__main__":
    main()
