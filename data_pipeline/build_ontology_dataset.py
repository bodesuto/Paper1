from pathlib import Path

from reasoning_ontology.src.dataset import build_ontology_dataset, save_ontology_dataset


def build_and_save_ontology_dataset(
    hil_classified_path: str | Path,
    rca_classified_path: str | Path | None,
    output_path: str | Path,
) -> Path:
    examples = build_ontology_dataset(hil_classified_path, rca_classified_path)
    return save_ontology_dataset(examples, output_path)
