from _experiment_presets import run_preset


if __name__ == "__main__":
    run_preset(agent="reflexion", mode="dual_memory", strategy="full", output_filename="reflexion_full.csv")
