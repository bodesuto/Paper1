import json
from pathlib import Path
from typing import Optional

from common.models import get_llm
from common.logger import get_logger
from classifier.prompts.classifier_prompts import HOTPOT_CLASSIFICATION_PROMPT


def classify_hotpot_vocab(question: str, llm=None):
	"""Classify HotpotQA question into reasoning intent, attributes, and entities.

	If `llm` is not provided, the function will create one via `common.models.get_llm()`.
	"""
	if llm is None:
		llm = get_llm()

	prompt = HOTPOT_CLASSIFICATION_PROMPT.format(question=question)
	response = llm.invoke(prompt)
	text = response.content.strip().replace("```json", "").replace("```", "").strip()
	try:
		return json.loads(text)
	except Exception:
		return {"intent": None, "attributes": [], "entities": [], "raw_output": text}



def process_hil_file(hil_path: Path, out_path: Optional[Path] = None, min_score: float = 3.0, llm=None):
    """Load a HIL JSON file, classify eligible questions, and write a classified output file.

    - `hil_path`: path to the `.hil.json` file (source)
    - `out_path`: optional path to write output. If not provided, will write to
      `<hil_filename>.classified.json` in the same directory.
    - `min_score`: minimum `review_score` (exclusive) to trigger classification.
    - `llm`: optional llm instance to pass to `classify_hotpot_vocab`.
    """
    logger = get_logger(__name__)

    if not hil_path.exists():
        logger.error("HIL file not found: %s", hil_path)
        raise FileNotFoundError(hil_path)

    if out_path is None:
        out_path = hil_path.with_name(hil_path.name + ".classified.json")

    logger.info("Reading HIL file: %s", hil_path)
    with hil_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        logger.error("Unexpected HIL format: expected a list at top level")
        raise ValueError("Unexpected HIL format: expected a list at top level")

    classified_count = 0
    out_entries = []
    for entry in data:
        try:
            score = entry.get("review_score")
            if score is None:
                continue

            try:
                numeric = float(score)
            except Exception:
                continue

            if numeric > float(min_score):
                question = entry.get("question")
                if not question:
                    continue
                logger.info("Classifying index %s (score=%s): %s", entry.get("index"), numeric, question)
                try:
                    vocab = classify_hotpot_vocab(question, llm=llm)
                except Exception as e:
                    logger.exception("Classification failed for index %s: %s", entry.get("index"), e)
                    vocab = {"error": str(e)}

                # append vocab and collect the entry to save
                entry["vocab"] = vocab
                out_entries.append(entry)
                classified_count += 1

        except Exception:
            logger.exception("Unexpected error processing entry: %s", entry)

    logger.info("Writing classified output (filtered) to %s", out_path)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out_entries, f, ensure_ascii=False, indent=2)

    logger.info("Classification complete. %d entries classified.", classified_count)
    return out_path, classified_count



def process_rca_insights(rca_path: Path, out_path: Optional[Path] = None, llm=None):
    """Process RCA insights from a given path: filter for status=false, classify questions, append vocab.

    - `rca_path`: path to the `.rca.json` file (source)
    - `out_path`: optional path to write output. If not provided, will write to
      `<rca_filename>.classified.json` in the same directory.
    - `llm`: optional llm instance to pass to `classify_hotpot_vocab`.
    """
    logger = get_logger(__name__)

    if not rca_path.exists():
        logger.error("RCA file not found: %s", rca_path)
        raise FileNotFoundError(rca_path)

    if out_path is None:
        out_path = rca_path.with_name(rca_path.name + ".classified.json")

    logger.info("Reading RCA file: %s", rca_path)
    with rca_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        logger.error("Unexpected RCA format: expected a list at top level")
        raise ValueError("Unexpected RCA format: expected a list at top level")

    classified_count = 0
    out_entries = []
    for entry in data:      
        try:
            status = entry.get("status")
            if status is not False:
                continue

            question = entry.get("question")
            if not question:
                continue
            logger.info("Classifying RCA index %s: %s", entry.get("index"), question)
            try:
                vocab = classify_hotpot_vocab(question, llm=llm)
            except Exception as e:
                logger.exception("Classification failed for RCA index %s: %s", entry.get("index"), e)
                vocab = {"error": str(e)}

            entry["vocab"] = vocab
            out_entries.append(entry)
            classified_count += 1

        except Exception:
            logger.exception("Unexpected error processing RCA entry: %s", entry)

    logger.info("Writing classified RCA output to %s", out_path)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out_entries, f, ensure_ascii=False, indent=2)

    logger.info("RCA Classification complete. %d entries classified.", classified_count)