import logging
from typing import Dict

class ParameterAutoTuner:
    """
    Module Meta-Learning để tự động điều chỉnh các tham số 
    Information Gain (beta) và Redundancy (gamma) dựa trên hiệu năng thực tế.
    """
    
    def __init__(self, initial_beta: float = 0.5, initial_gamma: float = 0.3):
        self.beta = initial_beta
        self.gamma = initial_gamma
        self.learning_rate = 0.01
        self.logger = logging.getLogger("AutoTuner")

    def tune(self, performance_metrics: Dict[str, float]):
        """
        Điều chỉnh tham số dựa trên các chỉ số hiệu năng từ Evaluation.
        - Nếu Redundancy Rate cao -> tăng Gamma.
        - Nếu Information Sufficiency thấp -> tăng Beta.
        """
        redundancy_rate = performance_metrics.get("redundancy_rate", 0.0)
        sufficiency_rate = performance_metrics.get("evidence_sufficiency", 1.0)
        
        if redundancy_rate > 0.4:
            self.gamma += self.learning_rate
            self.logger.info(f"Tăng Redundancy Penalty (Gamma) lên: {self.gamma:.4f}")
            
        if sufficiency_rate < 0.6:
            self.beta += self.learning_rate
            self.logger.info(f"Tăng Information Utility (Beta) lên: {self.beta:.4f}")

    def get_params(self) -> Dict[str, float]:
        return {
            "beta": self.beta,
            "gamma": self.gamma
        }

class HILTrigger:
    """Kích hoạt sự can thiệp của con người dựa trên độ bất định toán học."""
    
    @staticmethod
    def should_request_help(cognitive_gap: float, attempt_count: int) -> bool:
        # Nếu sau 2 lần thử mà mâu thuẫn vẫn > 0.8
        return cognitive_gap > 0.8 and attempt_count >= 2
