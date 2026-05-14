import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Thêm root vào path
sys.path.insert(0, str(Path(__file__).parent.parent))
from diagnostics.src.visualizer import PaperVisualizer

def generate_all_plots():
    viz = PaperVisualizer()
    print(">>> Đang khởi tạo dữ liệu trực quan...")

    # 1. Dữ liệu giả lập cho Radar Chart (Thay bằng dữ liệu thật từ eval_data)
    radar_data = pd.DataFrame({
        'Model': ['DualMemoryKG', 'GraphRAG', 'Self-RAG', 'VectorRAG'],
        'Accuracy': [0.85, 0.82, 0.78, 0.65],
        'Groundedness': [0.92, 0.75, 0.80, 0.50],
        'Efficiency': [0.88, 0.40, 0.60, 0.95],
        'Interpretability': [0.95, 0.70, 0.65, 0.30],
        'Stability': [0.90, 0.80, 0.75, 0.60]
    })
    viz.plot_sota_comparison_radar(radar_data, radar_data['Model'].tolist())
    print("- Đã tạo: sota_comparison_radar.png")

    # 2. Dữ liệu Information Plane
    plane_data = pd.DataFrame({
        'Model': ['DualMemoryKG']*10 + ['GraphRAG']*10 + ['VectorRAG']*10,
        'Tokens': np.concatenate([np.random.normal(500, 50, 10), np.random.normal(2000, 200, 10), np.random.normal(200, 20, 10)]),
        'InformationGain': np.concatenate([np.random.normal(0.8, 0.05, 10), np.random.normal(0.75, 0.05, 10), np.random.normal(0.4, 0.1, 10)])
    })
    viz.plot_information_plane(plane_data)
    print("- Đã tạo: information_plane.png")

    # 3. Dữ liệu Entropy Convergence
    steps = [0, 1, 2, 3, 4]
    entropy = [2.5, 1.8, 0.9, 0.3, 0.15]
    viz.plot_entropy_convergence(steps, entropy)
    print("- Đã tạo: entropy_convergence.png")

    # 4. Dữ liệu Ablation Matrix
    ablation_matrix = np.array([
        [1.0, 0.8, 0.7, 0.6],
        [0.8, 0.85, 0.6, 0.5],
        [0.7, 0.6, 0.75, 0.4],
        [0.6, 0.5, 0.4, 0.65]
    ])
    labels = ['Full', 'No-Graph', 'No-Ontology', 'No-Equilibrium']
    viz.plot_ablation_heatmap(ablation_matrix, labels)
    print("- Đã tạo: ablation_heatmap.png")

    # 5. Dữ liệu Manifold Projection (Giả lập 100 điểm với 5 cụm)
    X_manifold = np.random.randn(100, 16)
    y_manifold = np.random.randint(0, 5, 100)
    ont_labels = ['Bridge', 'Clarify', 'Extract', 'Summarize', 'Cross-verify']
    viz.plot_manifold_projection(X_manifold, y_manifold, ont_labels)
    print("- Đã tạo: manifold_projection.png")

    # 6. Dữ liệu Synaptic Evolution (Gia tăng trọng số)
    weights_history = [
        np.cumsum(np.random.normal(0.05, 0.02, 20)) + 1.0,
        np.cumsum(np.random.normal(0.03, 0.01, 20)) + 1.0,
        np.cumsum(np.random.normal(0.08, 0.03, 20)) + 1.0
    ]
    viz.plot_synaptic_weights_growth(weights_history)
    print("- Đã tạo: synaptic_evolution.png")

    # 7. Dữ liệu Error Composition
    errors = {
        'E-Ont (Ontology)': 15,
        'E-Trav (Traversal)': 25,
        'E-Gnd (Grounding)': 10,
        'E-KB (Knowledge)': 40,
        'Success': 10  # Để biểu đồ Pie phản ánh tổng thể
    }
    viz.plot_error_composition(errors)
    print("- Đã tạo: error_composition_pie.png")

    print("\n>>> TẤT CẢ BIỂU ĐỒ ĐÃ ĐƯỢC LƯU TẠI: reports/figures/")

if __name__ == "__main__":
    generate_all_plots()
