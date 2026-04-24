import sys
from pathlib import Path

# Add parent directory to path so we can import common
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import LANGFUSE_ENVIRONMENT, LANGFUSE_TRACE_NAME, OUTPUT_PATH
from log_transformation.src.log_extractor import export_runs
from common.logger import get_logger
logger = get_logger(__name__)


def main():
    logger.info("Starting Langfuse trace export")

    try:
        export_runs(
            output_path=OUTPUT_PATH,
            trace_name=LANGFUSE_TRACE_NAME,
            environment=LANGFUSE_ENVIRONMENT,
        )
        logger.info("Langfuse export completed successfully")

    except Exception as e:
        logger.exception("Export failed: %s", str(e))
        raise


if __name__ == "__main__":
    main()
