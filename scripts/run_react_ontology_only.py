from _experiment_presets import run_preset


if __name__ == "__main__":
    run_preset(agent="react", mode="dual_memory", strategy="ontology_only", output_filename="react_ontology_only.csv")
