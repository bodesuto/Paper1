import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import DATA_PATH, DATASET_SPLIT_SEED, OUTPUT_PATH, TRAVERSAL_SPLIT_MANIFEST_PATH
from data_pipeline.build_policy_dataset import build_policy_dataset_from_retrieval_logs
from data_pipeline.split_datasets import save_grouped_splits


def main():
    parser = argparse.ArgumentParser(description="Build traversal-policy dataset from retrieval experiment logs.")
    parser.add_argument(
        "--input-path",
        default=os.path.join(DATA_PATH, "react_dual_mem_results.csv"),
    )
    parser.add_argument(
        "--output-path",
        default=str(Path(OUTPUT_PATH).with_suffix(".traversal_policy_dataset.json")),
    )
    args = parser.parse_args()

    output_path, episodes = build_policy_dataset_from_retrieval_logs(args.input_path, args.output_path)
    split_outputs = save_grouped_splits(
        episodes,
        output_base_path=output_path,
        manifest_path=TRAVERSAL_SPLIT_MANIFEST_PATH,
        key_fields=("question",),
        seed=DATASET_SPLIT_SEED,
    )
    print(f"Saved traversal-policy dataset: {output_path}")
    print(f"Saved leakage-safe splits: train={split_outputs['train']} val={split_outputs['val']} test={split_outputs['test']}")


if __name__ == "__main__":
    main()
