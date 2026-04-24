import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import DATASET_SPLIT_SEED, ONTOLOGY_SPLIT_MANIFEST_PATH, OUTPUT_PATH
from common.logger import get_logger
from data_pipeline.split_datasets import save_grouped_splits
from reasoning_ontology.src.dataset import build_ontology_dataset, save_ontology_dataset


logger = get_logger(__name__)


def main():
    hil_path = Path(OUTPUT_PATH).with_suffix(".classified.json")
    rca_path = Path(OUTPUT_PATH).with_suffix(".classified_insights.json")
    output_path = Path(OUTPUT_PATH).with_suffix(".ontology_dataset.json")
    manifest_path = Path(ONTOLOGY_SPLIT_MANIFEST_PATH)

    examples = build_ontology_dataset(hil_path, rca_path if rca_path.exists() else None)
    save_ontology_dataset(examples, output_path)
    split_outputs = save_grouped_splits(
        [example.to_dict() for example in examples],
        output_base_path=output_path,
        manifest_path=manifest_path,
        key_fields=("question",),
        seed=DATASET_SPLIT_SEED,
    )

    logger.info("Built ontology dataset with %d examples -> %s", len(examples), output_path)
    logger.info(
        "Saved leakage-safe ontology splits: train=%s | val=%s | test=%s | manifest=%s",
        split_outputs["train"],
        split_outputs["val"],
        split_outputs["test"],
        split_outputs["manifest"],
    )


if __name__ == "__main__":
    main()
