from pathlib import Path
import sys

# Add parent directory to path so we can import common
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import OUTPUT_PATH
from common.logger import get_logger
from diagnostics.rca.src.rca import rca_for_all, load_traces_from_txt

logger = get_logger(__name__)

def main():
    in_traces_path = Path(OUTPUT_PATH).with_suffix(".react.txt")
    out_traces_path = Path(OUTPUT_PATH).with_suffix(".rca.json") # <-- set yours

    traces = load_traces_from_txt(in_traces_path)
    diagnostics = rca_for_all(traces, output_path=out_traces_path)

    logger.info("Wrote diagnostics for %d episodes -> %s", len(traces), out_traces_path)
    logger.info("Sample diagnostic: %s", diagnostics[0] if diagnostics else "None")


if __name__ == "__main__":
    main()
