from pathlib import Path
import argparse
import json
import sys
import time

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agents.prompts.hotpot_examples import react_examples
from agents.src.reflexion import reflexion_agent_run
from common.logger import get_logger


logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Cheap Reflexion smoke test without DeepEval or Neo4j."
    )
    parser.add_argument(
        "--data-path",
        default="./eval/data/mini_validation_3.csv",
        help="CSV file with question and answer columns.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1,
        help="Maximum number of rows to run.",
    )
    parser.add_argument(
        "--output-path",
        default="./eval/data/reflexion_smoke_results.csv",
        help="Where to save smoke test results.",
    )
    args = parser.parse_args()

    data_path = REPO_ROOT / Path(args.data_path)
    output_path = REPO_ROOT / Path(args.output_path)

    df = pd.read_csv(data_path).head(args.limit)
    logger.info("Loaded %d rows from %s", len(df), data_path)

    results = []

    for i, row in df.iterrows():
        question = row["question"]
        gold_answer = row.get("answer", "")

        started = time.perf_counter()
        answer, debug = reflexion_agent_run(question, examples=react_examples)
        latency_s = time.perf_counter() - started
        matched = bool(gold_answer) and str(gold_answer) in answer

        record = {
            "index": row.get("id", i),
            "question": question,
            "gold_answer": gold_answer,
            "predicted_answer": answer,
            "matched_substring": matched,
            "latency_s": latency_s,
            "first_answer": debug.get("first_answer", ""),
            "reflection": debug.get("reflection", ""),
            "second_answer": debug.get("second_answer", ""),
            "debug_json": json.dumps(debug, ensure_ascii=False),
        }
        results.append(record)

        print("---")
        print(f"IDX: {record['index']}")
        print(f"Q: {question}")
        print(f"GOLD: {gold_answer}")
        print(f"PRED: {answer}")
        print(f"LATENCY_S: {latency_s:.2f}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(output_path, index=False)
    logger.info("Saved smoke results -> %s", output_path)


if __name__ == "__main__":
    main()
