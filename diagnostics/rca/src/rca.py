
# Root-Cause Analysis and Feedback
from pathlib import Path
from typing import Any, Dict, List
from common.logger import get_logger
from common.models import get_llm
from ..prompts.diagnostic_prompts import DIAGNOSE_REACT_TRACE_PROMPT
import json

logger = get_logger(__name__)

def rca_for_run(trace_text: str):
    prompt = DIAGNOSE_REACT_TRACE_PROMPT.format(trace=trace_text)
    resp = get_llm().invoke(prompt)
    raw = resp.content.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except Exception:
        return {
            "success": False,
            "root_cause": "other",
            "explanation": "Non-JSON or malformed output from diagnostic model.",
            "insights": "Enforce JSON-only formatting with a stricter output parser."
        }


def rca_for_all(traces: List[str],
    output_path: str | Path,) -> List[Dict[str, Any]]:
    """
    Run RCA over all episodes in a LangSmith export.

    Returns list of:
        {
            "question": str,
            "trace": str,
            "diagnostic": dict
        }
    """
    results = []

    for trace in traces:
        question=trace.split("Question: ")[1].split("\nThought:")[0]

        # Skip empty traces
        if not trace or "Thought:" not in trace:
            logger.debug("Skipping question %s (no reasoning trace)", question)
            continue

        try:
            diagnostic = rca_for_run(trace)
        except Exception as e:
            logger.exception("RCA failed for question %s", question)
            diagnostic = {
                "error": str(e),
                "status": "failed"
            }

        results.append({
            "question": question,
            "trace": trace,
            "status": diagnostic.get("success", False),
            "rca": diagnostic,
        })

    logger.info("RCA completed for %d runs", len(results))

    # -------- Save --------
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info("Saved RCA results to %s", output_path)
    return results

    
def load_traces_from_txt(path: str | Path) -> List[str]:
    """
    Load previously exported ReAct traces from text file.

    Expects traces separated by:
        \n\n================================================================================\n\n
    """
    
    TRACE_SEPARATOR = "\n\n" + "=" * 80 + "\n\n"
    path = Path(path)

    if not path.exists():
        logger.error("Trace file not found: %s", path)
        return []

    with path.open("r", encoding="utf-8") as f:
        data = f.read()

    traces = [t.strip() for t in data.split(TRACE_SEPARATOR) if t.strip()]

    logger.info("Loaded %d traces from %s", len(traces), path)
    return traces