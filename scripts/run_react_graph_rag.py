from _experiment_presets import run_preset


if __name__ == "__main__":
    run_preset(agent="react", mode="dual_memory", strategy="graph_rag", output_filename="react_graph_rag.csv")
