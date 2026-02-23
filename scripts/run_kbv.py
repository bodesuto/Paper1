from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import OUTPUT_PATH
from diagnostics.kbv.src.kbv import load_traces_from_json, score_traces
from common.logger import get_logger

logger = get_logger(__name__)

def main():
    traces_path = Path(OUTPUT_PATH).with_suffix(".rca.json")
    out_json = Path(OUTPUT_PATH).with_suffix(".kbv.json")
    traces = load_traces_from_json(traces_path)
    logger.info("Loaded %d traces", len(traces))

    score_traces(
        traces=traces,
        output_path=out_json,
    )


if __name__ == "__main__":
    main()
