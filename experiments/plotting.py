from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


METRIC_LABELS = {
    "exact_match_eval": "Exact Match",
    "faithfulness_score": "Faithfulness",
    "path_grounding_precision": "Path Grounding",
    "unsupported_reasoning_score": "Unsupported",
    "evidence_f1": "Evidence F1",
    "total_latency_s": "Latency (s)",
}


def _method_name(path_value: str) -> str:
    stem = Path(str(path_value)).stem
    for prefix in ("react_", "reflexion_"):
        if stem.startswith(prefix):
            stem = stem[len(prefix):]
    return stem


def _load_summary(summary_csv: str | Path) -> pd.DataFrame:
    df = pd.read_csv(summary_csv)
    if "file" in df.columns:
        df["method"] = df["file"].map(_method_name)
    elif "retrieval_strategy" in df.columns:
        df["method"] = df["retrieval_strategy"]
    else:
        df["method"] = [f"method_{idx}" for idx in range(len(df))]
    return df


def plot_main_metrics(summary_csv: str | Path, output_path: str | Path) -> Path:
    df = _load_summary(summary_csv)
    metrics = ["exact_match_eval", "faithfulness_score", "path_grounding_precision"]
    plot_rows: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        for metric in metrics:
            if metric in row and pd.notna(row[metric]):
                plot_rows.append({"method": row["method"], "metric": METRIC_LABELS[metric], "value": float(row[metric])})
    plot_df = pd.DataFrame(plot_rows)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 5))
    sns.barplot(data=plot_df, x="method", y="value", hue="metric", palette="colorblind")
    plt.xticks(rotation=25, ha="right")
    plt.ylabel("Score")
    plt.xlabel("")
    plt.title("Main Metrics Across Retrieval Strategies")
    plt.tight_layout()
    plt.savefig(output_path, dpi=220)
    plt.close()
    return output_path


def plot_grounding_latency_tradeoff(summary_csv: str | Path, output_path: str | Path) -> Path:
    df = _load_summary(summary_csv)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))
    sns.scatterplot(
        data=df,
        x="total_latency_s",
        y="unsupported_reasoning_score",
        size="exact_match_eval",
        hue="method",
        palette="colorblind",
        sizes=(80, 250),
    )
    for _, row in df.iterrows():
        plt.text(float(row["total_latency_s"]), float(row["unsupported_reasoning_score"]), str(row["method"]), fontsize=8)
    plt.xlabel("Average Total Latency (s)")
    plt.ylabel("Unsupported Reasoning Rate")
    plt.title("Grounding-Latency Tradeoff")
    plt.tight_layout()
    plt.savefig(output_path, dpi=220)
    plt.close()
    return output_path


def plot_ablation_heatmap(summary_csv: str | Path, output_path: str | Path) -> Path:
    df = _load_summary(summary_csv)
    heatmap_cols = ["exact_match_eval", "faithfulness_score", "path_grounding_precision", "unsupported_reasoning_score"]
    pivot = df.set_index("method")[heatmap_cols].rename(columns=METRIC_LABELS)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, max(4, 0.55 * len(pivot))))
    sns.heatmap(pivot, annot=True, fmt=".3f", cmap="YlGnBu", cbar=True)
    plt.title("Ablation Heatmap")
    plt.tight_layout()
    plt.savefig(output_path, dpi=220)
    plt.close()
    return output_path


def _parse_json_field(value: Any, default):
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
        try:
            return json.loads(value)
        except Exception:
            return default
    return default


def plot_selector_objective_terms(results_csv: str | Path, output_path: str | Path) -> Path | None:
    df = pd.read_csv(results_csv)
    terms = {
        "concept_gain": [],
        "support_gain": [],
        "diversity_gain": [],
        "redundancy_cost": [],
        "selection_cost": [],
    }

    for row in df.to_dict(orient="records"):
        traversal = _parse_json_field(row.get("traversal"), {})
        for decision in traversal.get("decisions", []):
            if not isinstance(decision, dict) or decision.get("action") != "select":
                continue
            for key in terms:
                if key in decision:
                    terms[key].append(float(decision[key]))

    summary = {key: (sum(values) / len(values)) for key, values in terms.items() if values}
    if not summary:
        return None

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4))
    sns.barplot(x=list(summary.keys()), y=list(summary.values()), palette="muted")
    plt.xticks(rotation=20, ha="right")
    plt.ylabel("Average Contribution")
    plt.title("Average Evidence Selector Objective Terms")
    plt.tight_layout()
    plt.savefig(output_path, dpi=220)
    plt.close()
    return output_path
