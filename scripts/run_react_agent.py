import os
from pathlib import Path
import sys

# Add parent directory to path so we can import common
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.config import DATA_PATH, RETRIEVAL_STRATEGY
from eval.test.react_test import test, test_dual_memory, train
from eval.test.load_data import load_hotpot_dataset


def main():
    if not os.path.exists(os.path.join(DATA_PATH, "hard_bridge_500_train.csv")):
        load_hotpot_dataset(
            split="train",
            question_type="bridge",
            level="hard",
            size=500,
            output_path=os.path.join(DATA_PATH, "hard_bridge_500_train.csv"),
        )

    if not os.path.exists(os.path.join(DATA_PATH, "hard_bridge_500_validation.csv")):
        load_hotpot_dataset(
            split="validation",
            question_type="bridge",
            level="hard",
            size=500,
            output_path=os.path.join(DATA_PATH, "hard_bridge_500_validation.csv"),
        )

    train(os.path.join(DATA_PATH, "hard_bridge_500_train.csv"))

    test(
        data_path=os.path.join(DATA_PATH, "hard_bridge_500_validation.csv"),
        output_path=os.path.join(DATA_PATH, "react_baseline_results.csv"),
    )

    test_dual_memory(
        data_path=os.path.join(DATA_PATH, "hard_bridge_500_validation.csv"),
        output_path=os.path.join(DATA_PATH, "react_dual_mem_results.csv"),
        retrieval_strategy=RETRIEVAL_STRATEGY,
    )

if __name__ == "__main__":
    main()
