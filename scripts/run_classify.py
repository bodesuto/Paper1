import sys
from pathlib import Path
import json
from typing import Any

# Add parent directory to path so we can import common
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import OUTPUT_PATH
from classifier.src.classifier import process_hil_file, process_rca_insights


def main():
    hil_path = Path(OUTPUT_PATH).with_suffix(".hil.json")
    rca_path = Path(OUTPUT_PATH).with_suffix(".rca.json")
    out_path = Path(OUTPUT_PATH).with_suffix(".classified.json")
    out_insights_path = Path(OUTPUT_PATH).with_suffix(".classified_insights.json")

    process_hil_file(hil_path, out_path=out_path)
    process_rca_insights(rca_path, out_insights_path)


if __name__ == "__main__":
    main()
