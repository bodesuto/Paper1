import sys
from pathlib import Path
import json

# Add parent directory to path so we can import common
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import OUTPUT_PATH
from common.logger import get_logger
from knowledge_graph.src.insert_obs_data import insert_classified_payloads


logger = get_logger(__name__)

def main():
    out_path = Path(OUTPUT_PATH).with_suffix(".classified.json")
    out_insights_path = Path(OUTPUT_PATH).with_suffix(".classified_insights.json")

    logger.info("Loading classified HIL entries from %s", out_path)
    with out_path.open("r", encoding="utf-8") as f:
        hil_data = json.load(f)
    logger.info("Loaded %d HIL entries", len(hil_data))

    logger.info("Loading classified RCA entries from %s", out_insights_path)
    with out_insights_path.open("r", encoding="utf-8") as f:
        rca_data = json.load(f)
    logger.info("Loaded %d RCA entries", len(rca_data))

    # Combine all payloads
    all_payloads = hil_data + rca_data
    logger.info("Total payloads to insert: %d", len(all_payloads))

    if all_payloads:
        inserted = insert_classified_payloads(all_payloads)
        logger.info("Insert complete. %d payloads inserted.", inserted)
    else:
        logger.warning("No payloads to insert.")


if __name__ == "__main__":
    main()
