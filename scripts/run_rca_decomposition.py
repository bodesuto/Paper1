import argparse
import json
import pandas as pd
from pathlib import Path
from collections import Counter

def main():
    parser = argparse.ArgumentParser(description="Generate Q1-grade Error Decomposition Summary.")
    parser.add_argument("--rca-json", required=True, help="Path to the RCA results JSON file.")
    parser.add_argument("--output-csv", default="output/error_decomposition_summary.csv", help="Path to save the summary CSV.")
    args = parser.parse_args()

    rca_path = Path(args.rca_json)
    if not rca_path.exists():
        print(f"Error: RCA file {rca_path} not found.")
        return

    with rca_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Error Taxonomy counts
    stats = {
        "ontology_mismatch": 0,
        "traversal_suboptimality": 0,
        "grounding_gap": 0,
        "knowledge_deficiency": 0,
        "reasoning_loop": 0,
        "timeout": 0,
        "success": 0,
        "other": 0
    }

    severities = []
    insights = []

    for item in data:
        rca = item.get("rca", {})
        cause = rca.get("root_cause", "other")
        if cause in stats:
            stats[cause] += 1
        else:
            stats["other"] += 1
        
        if "severity" in rca:
            severities.append(rca["severity"])
        
        if rca.get("mechanism_insight"):
            insights.append(rca["mechanism_insight"])

    total = len(data)
    summary_rows = []
    for cause, count in stats.items():
        summary_rows.append({
            "Error Type": cause,
            "Count": count,
            "Percentage": (count / total * 100) if total > 0 else 0,
            "Avg Severity": sum(severities) / len(severities) if severities and cause != "success" else 0
        })

    df = pd.DataFrame(summary_rows)
    
    # Save the summary
    output_path = Path(args.output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print("\n" + "="*50)
    print("Q1 ERROR DECOMPOSITION SUMMARY")
    print("="*50)
    print(df.to_string(index=False))
    print("="*50)
    print(f"Summary saved to: {output_path}")

    # Top Mechanism Insights
    print("\nTOP MECHANISM INSIGHTS FOR SYSTEM IMPROVEMENT:")
    common_insights = Counter(insights).most_common(3)
    for insight, count in common_insights:
        print(f"- [{count}] {insight}")

if __name__ == "__main__":
    main()
