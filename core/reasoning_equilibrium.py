import numpy as np
from typing import Dict, List, Tuple

class ReasoningEquilibrium:
    """
    Module phân xử mâu thuẫn giữa Kiến thức nội tại (LLM Internal) 
    và Bằng chứng bên ngoài (KG External). 
    Đảm bảo tính "Trung thực" (Honesty) và "Groundedness" cho hệ thống.
    """
    
    def __init__(self, conflict_threshold: float = 0.7):
        self.threshold = conflict_threshold

    def calculate_knowledge_gap(self, llm_confidence: float, evidence_strength: float) -> float:
        """
        Tính toán khoảng cách nhận thức (Cognitive Gap).
        Gap cao = Mâu thuẫn cao giữa suy luận và thực tế.
        """
        # Sử dụng hàm Sigmoid để chuẩn hóa
        gap = abs(llm_confidence - evidence_strength)
        return gap

    def arbitrator(self, internal_claim: str, external_evidences: List[str], 
                  llm_logits: Dict[str, float]) -> Dict:
        """
        Phân xử dựa trên lý thuyết Information Bottleneck.
        Trả về chiến lược: 'TRUST_EXTERNAL', 'TRUST_INTERNAL', hoặc 'DOUBT_AND_RETRY'.
        """
        # Giả lập việc đo lường độ tự tin dựa trên Entropy của Logits
        internal_entropy = -sum(p * np.log(p) for p in llm_logits.values() if p > 0)
        internal_confidence = 1.0 / (1.0 + internal_entropy) # Entropy thấp = Confidence cao
        
        # Độ mạnh của bằng chứng bên ngoài (trung bình synaptic_weight)
        # Giả định evidence_strength đã được tính toán từ traversal policy
        evidence_strength = np.mean([float(e.split('|')[-1]) if '|' in e else 0.5 for e in external_evidences])
        
        gap = self.calculate_knowledge_gap(internal_confidence, evidence_strength)
        
        decision = "TRUST_EXTERNAL"
        if gap > self.threshold:
            decision = "DOUBT_AND_RETRY" 
        elif internal_confidence > 0.9 and evidence_strength < 0.3:
            decision = "TRUST_INTERNAL" # Cân nhắc trường hợp LLM biết rõ hơn (ít gặp)

        return {
            "decision": decision,
            "cognitive_gap": gap,
            "internal_confidence": internal_confidence,
            "external_evidence_strength": evidence_strength,
            "action_required": decision == "DOUBT_AND_RETRY"
        }

    def get_honesty_score(self, history: List[Dict]) -> float:
        """Tính điểm 'Trung thực' dựa trên số lần hệ thống chọn tin vào bằng chứng đúng"""
        if not history: return 1.0
        trust_scores = [1.0 - h['cognitive_gap'] for h in history]
        return np.mean(trust_scores)
