import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import OUTPUT_PATH, TRAVERSAL_POLICY_PATH, TRAVERSAL_TOP_K, TRAVERSAL_TRAIN_SPLIT
from traversal_policy.src.train import fit_and_save_policy


def main():
    parser = argparse.ArgumentParser(description="Fit a pairwise-ranked traversal policy checkpoint from policy episodes.")
    split_default = Path(OUTPUT_PATH).with_suffix(f".traversal_policy_dataset.{TRAVERSAL_TRAIN_SPLIT}.json")
    parser.add_argument(
        "--input-path",
        default=str(split_default if split_default.exists() else Path(OUTPUT_PATH).with_suffix(".traversal_policy_dataset.json")),
    )
    parser.add_argument(
        "--output-path",
        default=TRAVERSAL_POLICY_PATH,
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=TRAVERSAL_TOP_K,
    )
    args = parser.parse_args()

    fit_and_save_policy(args.input_path, args.output_path, top_k=args.top_k)


if __name__ == "__main__":
    main()
