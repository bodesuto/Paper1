import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from eval.test.transfer_eval import summarize_transfer_runs


def main():
    parser = argparse.ArgumentParser(description="Summarize in-domain vs out-of-domain result CSVs for transfer analysis.")
    parser.add_argument("--in-domain", required=True)
    parser.add_argument("--out-of-domain", nargs="+", required=True)
    parser.add_argument("--output-path", required=True)
    args = parser.parse_args()

    summarize_transfer_runs(args.in_domain, args.out_of_domain, output_path=args.output_path)


if __name__ == "__main__":
    main()
