import numpy as np
from typing import List, Dict

class InformationBottleneckAnalytic:
    """
    Công cụ phân tích dựa trên nguyên lý Information Bottleneck (IB).
    Đo lường sự cân bằng giữa:
    1. Compression (Nén): Giảm thiểu thông tin dư thừa từ dữ liệu đầu vào X.
    2. Prediction (Dự đoán): Giữ lại tối đa thông tin hữu ích cho câu trả lời Y.
    """
    
    def __init__(self):
        self.points = []

    def log_state(self, input_complexity: float, reasoning_utility: float, step: int):
        """
        Ghi lại trạng thái tại một bước lập luận.
        - input_complexity: I(X; Z) - lượng thông tin nạp vào context.
        - reasoning_utility: I(Z; Y) - giá trị thông tin đóng góp cho đáp án.
        """
        self.points.append({
            "step": step,
            "complexity": input_complexity,
            "utility": reasoning_utility
        })

    def calculate_ib_efficiency(self) -> float:
        """
        Tính toán hiệu suất IB (Beta-efficiency).
        Hệ thống tối ưu khi Utility cao trên một đơn vị Complexity thấp.
        """
        if not self.points: return 0.0
        
        comps = [p['complexity'] for p in self.points]
        utils = [p['utility'] for p in self.points]
        
        # Hiệu suất = Area under Information Plane
        efficiency = np.mean(utils) / (np.mean(comps) + 1e-9)
        return float(efficiency)

    def generate_scientific_plot_data(self) -> Dict:
        """Xuất dữ liệu để vẽ biểu đồ Information Plane trong bài báo"""
        return {
            "x_axis_complexity": [p['complexity'] for p in self.points],
            "y_axis_utility": [p['utility'] for p in self.points],
            "labels": [f"Step {p['step']}" for p in self.points],
            "overall_efficiency": self.calculate_ib_efficiency()
        }
