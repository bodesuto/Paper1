from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=str(cwd), check=True)


def run_theorem_aligned_suite(
    *,
    repo_root: str | Path,
    agent: str,
    data_path: str,
    output_dir: str,
    annotations_path: str | None = None,
    bootstrap_samples: int = 1000,
) -> None:
    repo_root = Path(repo_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    python = sys.executable

    ablation_dir = output_dir / "ablations"
    ablation_dir.mkdir(parents=True, exist_ok=True)
    summary_csv = output_dir / f"{agent}_theorem_summary.csv"
    transfer_csv = output_dir / f"{agent}_transfer_summary.csv"
    stress_csv = output_dir / f"{agent}_stress_noisy.csv"
    figures_dir = output_dir / "figures"
    baseline_csv = ablation_dir / f"{agent}_baseline.csv"
    full_csv = ablation_dir / f"{agent}_full.csv"

    _run([python, "scripts/run_ablation_suite.py", "--agent", agent, "--data-path", data_path, "--output-dir", str(ablation_dir)], repo_root)
    _run(
        [
            python,
            "scripts/run_stress_suite.py",
            "--agent",
            agent,
            "--strategy",
            "full",
            "--stress",
            "noisy",
            "--data-path",
            data_path,
            "--output-path",
            str(stress_csv),
        ],
        repo_root,
    )
    _run(
        [
            python,
            "scripts/run_transfer_eval.py",
            "--in-domain",
            str(full_csv),
            "--out-of-domain",
            str(stress_csv),
            "--output-path",
            str(transfer_csv),
        ],
        repo_root,
    )

    inputs = [
        str(ablation_dir / f"{agent}_baseline.csv"),
        str(ablation_dir / f"{agent}_heuristic.csv"),
        str(ablation_dir / f"{agent}_vector_rag.csv"),
        str(ablation_dir / f"{agent}_graph_rag.csv"),
        str(ablation_dir / f"{agent}_ontology_only.csv"),
        str(ablation_dir / f"{agent}_traversal_only.csv"),
        str(ablation_dir / f"{agent}_learned.csv"),
    ]
    if full_csv.exists():
        inputs.append(str(full_csv))
    _run(
        [
            python,
            "scripts/run_result_summary.py",
            "--inputs",
            *inputs,
            "--reference",
            str(baseline_csv),
            "--bootstrap-samples",
            str(bootstrap_samples),
            "--output-path",
            str(summary_csv),
        ],
        repo_root,
    )

    if annotations_path:
        evidence_eval_csv = output_dir / f"{agent}_annotated_evidence_eval.csv"
        evidence_eval_summary = output_dir / f"{agent}_annotated_evidence_summary.json"
        target_csv = full_csv if full_csv.exists() else baseline_csv
        _run(
            [
                python,
                "scripts/run_annotated_evidence_eval.py",
                "--results-csv",
                str(target_csv),
                "--annotations-path",
                annotations_path,
                "--output-path",
                str(evidence_eval_csv),
                "--summary-path",
                str(evidence_eval_summary),
            ],
            repo_root,
        )

    figure_results_csv = full_csv if full_csv.exists() else baseline_csv
    _run(
        [
            python,
            "scripts/run_paper_figures.py",
            "--summary-csv",
            str(summary_csv),
            "--results-csv",
            str(figure_results_csv),
            "--output-dir",
            str(figures_dir),
        ],
        repo_root,
    )
