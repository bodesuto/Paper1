import json
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import ONTOLOGY_TRAIN_SPLIT, OUTPUT_PATH
from common.logger import get_logger
from reasoning_ontology.src.dataset import OntologyTrainingExample
from reasoning_ontology.src.prototype_learner import WeakLabelPrototypeLearner


logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Fit ontology prototypes on a leakage-safe split.")
    parser.add_argument("--split", default=ONTOLOGY_TRAIN_SPLIT, choices=["train", "val", "test", "full"])
    parser.add_argument("--input-path", default=None)
    parser.add_argument("--output-path", default=str(Path(OUTPUT_PATH).with_suffix(".ontology_prototypes.json")))
    args = parser.parse_args()

    default_dataset = Path(OUTPUT_PATH).with_suffix(".ontology_dataset.json")
    split_dataset = default_dataset.with_suffix(f".{args.split}.json")
    dataset_path = Path(args.input_path) if args.input_path else (split_dataset if args.split != "full" and split_dataset.exists() else default_dataset)
    output_path = Path(args.output_path)

    if not dataset_path.exists():
        raise FileNotFoundError(f"Ontology dataset not found: {dataset_path}")

    with dataset_path.open("r", encoding="utf-8") as handle:
        raw_examples = json.load(handle)

    examples = [OntologyTrainingExample(**item) for item in raw_examples]
    learner = WeakLabelPrototypeLearner()
    prototypes = learner.fit(examples)
    learner.save(output_path)

    logger.info("Fitted %d adaptive ontology prototypes on split=%s -> %s", len(prototypes), args.split, output_path)
    logger.info(
        "If you want learned ontology assignments persisted into Neo4j nodes, rerun scripts/run_insert_obs.py after this step."
    )


if __name__ == "__main__":
    main()
