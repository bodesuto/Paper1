# Data Pipeline

This folder contains dataset-preparation utilities for the research extensions of `DualMemoryKG`.

Current scope:

- split exported ontology datasets into train/validation/test files
- keep training data preparation separate from online agent/runtime code

Recommended usage:

1. run `scripts/run_classify.py`
2. run `scripts/run_build_ontology_dataset.py`
3. use `data_pipeline/split_datasets.py` to create experiment splits
