import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.plotting import (
    plot_ablation_heatmap,
    plot_grounding_latency_tradeoff,
    plot_main_metrics,
    plot_selector_objective_terms,
)


def main():
    parser = argparse.ArgumentParser(description="Generate publication-style figures from summary/result CSVs.")
    parser.add_argument("--summary-csv", required=True)
    parser.add_argument("--results-csv", default=None, help="Optional detailed result CSV for selector-term figure.")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_main_metrics(args.summary_csv, output_dir / "fig_main_metrics.png")
    plot_grounding_latency_tradeoff(args.summary_csv, output_dir / "fig_grounding_latency_tradeoff.png")
    plot_ablation_heatmap(args.summary_csv, output_dir / "fig_ablation_heatmap.png")
    if args.results_csv:
        plot_selector_objective_terms(args.results_csv, output_dir / "fig_selector_objective_terms.png")


if __name__ == "__main__":
    main()
