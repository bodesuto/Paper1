# Experiments

This folder hosts paper-facing experiment orchestration and figure generation.

## Main workflows

- theorem-aligned suite:
  - `scripts/run_theorem_experiment_suite.py`
- figure generation:
  - `scripts/run_paper_figures.py`
- evidence annotation bootstrap:
  - `scripts/run_prepare_evidence_annotation.py`
- evidence-grounding evaluation:
  - `scripts/run_annotated_evidence_eval.py`
- architecture-validity and error-decomposition report:
  - `scripts/run_architecture_validity.py`

## Suggested order

1. Run ablations or the theorem suite.
2. Export a subset of result rows for manual evidence annotation.
3. Fill `gold_evidence_node_ids`, `sufficient_evidence_sets`, and `contradiction_node_ids`.
4. Run annotated evidence evaluation.
5. Build architecture-validity / error-decomposition analysis.
6. Generate paper figures from the summary CSV and detailed result CSV.

## Example

```powershell
python .\scripts\run_prepare_evidence_annotation.py --results-csv .\eval\data\ablations\react_full.csv --output-path .\experiments\react_full_annotations.json --limit 100
python .\scripts\run_annotated_evidence_eval.py --results-csv .\eval\data\ablations\react_full.csv --annotations-path .\experiments\react_full_annotations.json --output-path .\experiments\react_full_evidence_eval.csv --summary-path .\experiments\react_full_evidence_eval_summary.json
python .\scripts\run_architecture_validity.py --summary-csv .\eval\data\react_summary.csv --results-csv .\eval\data\ablations\react_full.csv --output-path .\experiments\react_architecture_validity.json --error-output-path .\experiments\react_architecture_error_breakdown.csv
python .\scripts\run_paper_figures.py --summary-csv .\eval\data\react_summary.csv --results-csv .\eval\data\ablations\react_full.csv --error-breakdown-csv .\experiments\react_architecture_error_breakdown.csv --output-dir .\experiments\figures
```
