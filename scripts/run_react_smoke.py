from pathlib import Path
import argparse
import json
import sys
import time

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agents.prompts.hotpot_examples import react_examples
from agents.src.react import creat_react_agent, format_examples, tool_calls
from common.logger import get_logger


logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Cheap ReAct smoke test without DeepEval or Neo4j."
    )
    parser.add_argument(
        "--data-path",
        default="./eval/data/mini_validation_3.csv",
        help="CSV file with question and answer columns.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Maximum number of rows to run.",
    )
    parser.add_argument(
        "--output-path",
        default="./eval/data/react_smoke_results.csv",
        help="Where to save smoke test results.",
    )
    args = parser.parse_args()

    data_path = REPO_ROOT / Path(args.data_path)
    output_path = REPO_ROOT / Path(args.output_path)

    df = pd.read_csv(data_path).head(args.limit)
    logger.info("Loaded %d rows from %s", len(df), data_path)

    agent = creat_react_agent()
    results = []

    for i, row in df.iterrows():
        tool_calls.clear()
        question = row["question"]
        gold_answer = row.get("answer", "")

        started = time.perf_counter()
        output = agent.invoke({"input": question, "examples": format_examples(react_examples)})
        latency_s = time.perf_counter() - started

        predicted = output.get("output", str(output)) if isinstance(output, dict) else str(output)
        matched = bool(gold_answer) and str(gold_answer) in predicted

        record = {
            "index": row.get("id", i),
            "question": question,
            "gold_answer": gold_answer,
            "predicted_answer": predicted,
            "matched_substring": matched,
            "latency_s": latency_s,
            "tool_calls_count": len(tool_calls),
            "tool_calls_json": json.dumps(tool_calls, ensure_ascii=False),
        }
        results.append(record)

        print("---")
        print(f"IDX: {record['index']}")
        print(f"Q: {question}")
        print(f"GOLD: {gold_answer}")
        print(f"PRED: {predicted}")
        print(f"TOOLS: {len(tool_calls)}")
        print(f"LATENCY_S: {latency_s:.2f}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(output_path, index=False)
    logger.info("Saved smoke results -> %s", output_path)


if __name__ == "__main__":
    main()
