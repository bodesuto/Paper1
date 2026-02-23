from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.logger import get_logger
from log_transformation.src.log_formatter import write_react_traces  # adjust import if needed
from common.config import OUTPUT_PATH  # your export json path from .env/config

logger = get_logger(__name__)


def main():
    in_json = Path(OUTPUT_PATH)

    # default: write next to the JSON
    out_txt = in_json.with_suffix(".react.txt")

    logger.info("Pruning ReAct traces")
    logger.info("Input JSON: %s", in_json)
    logger.info("Output TXT: %s", out_txt)

    write_react_traces(in_json_path=in_json, out_txt_path=out_txt)
   
    logger.info("Done")


if __name__ == "__main__":
    main()
