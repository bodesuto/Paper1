import math
from typing import List, Dict
import numpy as np

class EntropyTracker:
    """
    Theo dõi Shannon Entropy và Marginal Information Gain (IG) 
    trong suốt quá trình duyệt đồ thị tri thức.
    """
    
    def __init__(self):
        self.history = []
        
    def calculate_shannon_entropy(self, probabilities: List[float]) -> float:
        """Tính H(X) = -sum(p * log2(p))"""
        probs = [p for p in probabilities if p > 0]
        if not probs:
            return 0.0
        return -sum(p * math.log2(p) for p in probs)

    def track_step(self, step_name: str, candidate_scores: List[float], selected_index: int):
        """
        Ghi lại một bước lập luận và tính toán sự thay đổi Entropy.
        
        Args:
            step_name: Tên bước (ví dụ: 'hop_1', 'hop_2')
            candidate_scores: Điểm số của các ứng viên (trước softmax)
            selected_index: Index của node được chọn
        """
        # Áp dụng Softmax để có phân phối xác suất
        exp_scores = np.exp(candidate_scores - np.max(candidate_scores))
        probs = exp_scores / exp_scores.sum()
        
        entropy_t = self.calculate_shannon_entropy(probs.tolist())
        
        # Marginal Information Gain thực diện
        # Trong thực tế, IG là sự sụt giảm entropy so với trạng thái trước
        prev_entropy = self.history[-1]['entropy'] if self.history else 2.0 # Giả định ban đầu là 2.0 bits
        ig = max(0, prev_entropy - entropy_t)
        
        self.history.append({
            "step": step_name,
            "entropy": entropy_t,
            "ig": ig,
            "selected_hit_prob": probs[selected_index]
        })

    def get_total_ig(self) -> float:
        """Tổng lượng thông tin thu thập được (bits)"""
        return sum(h['ig'] for h in self.history)

    def get_summary(self) -> Dict:
        """Trả về tóm tắt phục vụ báo cáo khoa học"""
        if not self.history:
            return {}
        
        total_ig = self.get_total_ig()
        avg_surprisal = np.mean([-math.log2(h['selected_hit_prob']) for h in self.history])
        
        return {
            "total_information_gain_bits": total_ig,
            "final_entropy": self.history[-1]['entropy'],
            "average_surprisal": avg_surprisal,
            "steps_count": len(self.history)
        }
