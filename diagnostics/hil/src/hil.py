import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from common.logger import get_logger

logger = get_logger(__name__)


def load_traces(
    input_path: str | Path,
    output_path: str | Path,
) -> List[Dict[str, Any]]:
    """
    Load traces for HIL.

    Behavior:
    - If output_path exists → return its content.
    - If not → load from input_path, assign stable IDs,
      save to output_path, and return.
    """

    input_path = Path(input_path)
    output_path = Path(output_path)

    # If already exists → load and return
    if output_path.exists():
        logger.info("Loading existing labeled file: %s", output_path)
        with output_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    # Otherwise initialize from input
    logger.info("Initializing new HIL file from: %s", input_path)

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Expected input JSON to be a list")

    initialized = []

    for i, item in enumerate(data):
        initialized.append(
            {
                "id": item.get("id") or str(i),
                "question": item.get("question", ""),
                "trace": item.get("trace", ""),
                "final_answer": item.get("actual_answer") or "",
                "ratings": {},   # for multi-reviewer system
            }
        )

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(initialized, f, indent=2)

    logger.info("Saved initialized HIL file → %s", output_path)

    return initialized


def load_reviews(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return {"reviews": {}}  # {trace_id: {reviewer_id: {rating, comment, ts}}}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        # File exists but is empty or invalid JSON; return default
        return {"reviews": {}}

def run_hil_app(traces: List[Dict[str, Any]], reviews_path: str | Path) -> None:
    logger.info("Starting HIL Streamlit app with %d traces", len(traces))
    app_path = Path(__file__).resolve().parent / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)], check=True)
