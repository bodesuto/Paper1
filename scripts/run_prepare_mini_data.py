from pathlib import Path
import argparse
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common.config import DATA_PATH
from common.logger import get_logger


logger = get_logger(__name__)


def build_mini_split(split: str, size: int) -> Path:
    data_dir = REPO_ROOT / DATA_PATH
    source = data_dir / f"hard_bridge_500_{split}.csv"
    target = data_dir / f"mini_{split}_{size}.csv"

    if not source.exists():
        raise FileNotFoundError(
            f"Missing source dataset: {source}. Run the full dataset download first."
        )

    df = pd.read_csv(source).head(size)
    target.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(target, index=False)

    logger.info("Wrote %d rows -> %s", len(df), target)
    return target


def main():
    parser = argparse.ArgumentParser(
        description="Create small train/validation CSV files for cheap smoke tests."
    )
    parser.add_argument("--size", type=int, default=3, help="Rows per mini split.")
    args = parser.parse_args()

    train_path = build_mini_split("train", args.size)
    validation_path = build_mini_split("validation", args.size)

    print(f"mini train: {train_path}")
    print(f"mini validation: {validation_path}")


if __name__ == "__main__":
    main()
