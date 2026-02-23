import sys
from anyio import Path
from common.config import LANGSMITH_PROJECT_ID, OUTPUT_PATH
from log_transformation.src.log_extractor import export_runs
from common.logger import get_logger

# Add parent directory to path so we can import common
sys.path.insert(0, str(Path(__file__).parent.parent))
logger = get_logger(__name__)


def main():
    logger.info("Starting LangSmith run export")

    try:
        export_runs(
            project_id=LANGSMITH_PROJECT_ID,
            output_path=OUTPUT_PATH
        )
        logger.info("LangSmith export completed successfully")

    except Exception as e:
        logger.exception("Export failed: %s", str(e))
        raise


if __name__ == "__main__":
    main()
