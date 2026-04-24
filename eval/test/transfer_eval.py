from __future__ import annotations

from pathlib import Path

import pandas as pd

from eval.test.result_summary import SUMMARY_COLUMNS, summarize_result_csv


def summarize_transfer_runs(
    in_domain_csv: str | Path,
    out_of_domain_csvs: list[str | Path],
    output_path: str | Path | None = None,
):
    in_domain_summary = summarize_result_csv(in_domain_csv)
    rows: list[dict[str, float | str]] = [
        {
            **in_domain_summary,
            "domain": "in_domain",
            "reference_file": str(Path(in_domain_csv)),
        }
    ]

    for csv_path in out_of_domain_csvs:
        out_summary = summarize_result_csv(csv_path)
        row: dict[str, float | str] = {
            **out_summary,
            "domain": "out_of_domain",
            "reference_file": str(Path(csv_path)),
        }
        for column in SUMMARY_COLUMNS:
            in_value = in_domain_summary.get(column)
            out_value = out_summary.get(column)
            if isinstance(in_value, (int, float)) and isinstance(out_value, (int, float)):
                row[f"{column}_delta_vs_in_domain"] = float(out_value) - float(in_value)
                if float(in_value) != 0.0:
                    row[f"{column}_retention_ratio"] = float(out_value) / float(in_value)
        rows.append(row)

    df = pd.DataFrame(rows)
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
    return df
