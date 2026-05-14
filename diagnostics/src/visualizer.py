import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

class PaperVisualizer:
    """Bộ công cụ tạo biểu đồ chuẩn học thuật cho bài báo Q1."""
    
    def __init__(self, style="whitegrid"):
        sns.set_theme(style=style)
        plt.rcParams.update({'font.size': 12, 'font.family': 'serif'})
        self.output_dir = Path("reports/figures")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_sota_comparison_radar(self, data: pd.DataFrame, models: list):
        """Vẽ biểu đồ Radar so sánh đa chiều với các SOTA."""
        categories = list(data.columns[1:])
        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        for model in models:
            values = data[data['Model'] == model].iloc[0, 1:].values.flatten().tolist()
            values += values[:1]
            ax.plot(angles, values, linewidth=2, linestyle='solid', label=model)
            ax.fill(angles, values, alpha=0.1)
            
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        plt.xticks(angles[:-1], categories)
        plt.title("DualMemoryKG vs SOTA: Holistic Evaluation", size=15, pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        
        plt.savefig(self.output_dir / "sota_comparison_radar.png", bbox_inches='tight', dpi=300)
        plt.close()

    def plot_information_plane(self, df: pd.DataFrame):
        """Vẽ Information Plane: Token Efficiency vs Information Gain."""
        plt.figure(figsize=(10, 6))
        scatter = sns.scatterplot(data=df, x="Tokens", y="InformationGain", hue="Model", style="Model", s=100)
        
        # Vẽ đường biên Pareto tiêu chuẩn (giả định)
        plt.title("Information Plane: Efficiency-Utility Trade-off", size=14)
        plt.xlabel("Resource Consumption (Tokens)")
        plt.ylabel("Reasoning Utility (Information Gain)")
        plt.grid(True, linestyle="--", alpha=0.6)
        
        plt.savefig(self.output_dir / "information_plane.png", dpi=300)
        plt.close()

    def plot_entropy_convergence(self, steps: list, entropy_values: list):
        """Vẽ biểu đồ hội tụ Entropy (Grounded Convergence)."""
        plt.figure(figsize=(8, 5))
        plt.plot(steps, entropy_values, marker='o', linewidth=2, color='coral', label='System Entropy')
        plt.axhline(y=0.1, color='gray', linestyle='--', label='Grounding Threshold')
        
        plt.title("Grounded Convergence: Uncertainty Decay", size=14)
        plt.xlabel("Reasoning Hops")
        plt.ylabel("Shannon Entropy (H)")
        plt.legend()
        
        plt.savefig(self.output_dir / "entropy_convergence.png", dpi=300)
        plt.close()

    def plot_ablation_heatmap(self, matrix: np.ndarray, labels: list):
        """Vẽ Heatmap cho thí nghiệm bóc tách (Ablation Study)."""
        plt.figure(figsize=(8, 6))
        sns.heatmap(matrix, annot=True, xticklabels=labels, yticklabels=labels, cmap="YlGnBu")
        plt.title("Ablation Study: Component Impact Heatmap", size=14)
        
        plt.savefig(self.output_dir / "ablation_heatmap.png", dpi=300)
        plt.close()

    def plot_manifold_projection(self, X: np.ndarray, y: list, labels: list):
        """Vẽ biểu đồ t-SNE/PCA cho không gian Latent Ontology."""
        plt.figure(figsize=(10, 7))
        from sklearn.manifold import TSNE
        if X.shape[1] > 2:
            X_emb = TSNE(n_components=2, random_state=42).fit_transform(X)
        else:
            X_emb = X
            
        scatter = plt.scatter(X_emb[:, 0], X_emb[:, 1], c=y, cmap='viridis', alpha=0.7)
        plt.colorbar(scatter, ticks=range(len(labels)), label="Ontology Strategy")
        plt.title("Latent Manifold Projection ($ \mathcal{Z} $ space)", size=14)
        
        plt.savefig(self.output_dir / "manifold_projection.png", dpi=300)
        plt.close()

    def plot_synaptic_weights_growth(self, weights_history: list):
        """Vẽ biểu đồ tiến hóa trọng số đồ thị (Synaptic Plasticity)."""
        plt.figure(figsize=(9, 5))
        for i, weight_path in enumerate(weights_history):
            plt.plot(weight_path, label=f"Refined Path {i+1}")
            
        plt.axhline(y=1.0, color='r', linestyle='--', label='Initial Weight')
        plt.title("Hebbian Evolution: Synaptic Weight Growth", size=14)
        plt.xlabel("Grounding Iterations")
        plt.ylabel("Synaptic Strength ($ w_{ij} $)")
        plt.legend()
        
        plt.savefig(self.output_dir / "synaptic_evolution.png", dpi=300)
        plt.close()

    def plot_error_composition(self, errors: dict):
        """Vẽ biểu đồ Error Composition (Scientific RCA)."""
        plt.figure(figsize=(8, 8))
        labels = list(errors.keys())
        sizes = list(errors.values())
        colors = sns.color_palette("pastel")[0:len(labels)]
        
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, explode=[0.05]*len(labels))
        plt.title("Scientific Error Decomposition Summary", size=14)
        
        plt.savefig(self.output_dir / "error_composition_pie.png", dpi=300)
        plt.close()
