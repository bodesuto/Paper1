from typing import List, Dict
import numpy as np

class EvidenceExplainer:
    """
    Module giải thích logic lựa chọn bằng chứng.
    Chuyển đổi các thông số toán học (IG, Surprisal, Weights) thành ngôn ngữ tự nhiên.
    """
    
    def __init__(self):
        pass

    def explain_selection(self, node_key: str, features: Dict[str, float], 
                         contribution_score: float) -> str:
        """
        Tạo lời giải thích cho việc tại sao một Node được chọn.
        """
        reasons = []
        
        if features.get('is_experience', 0) > 0:
            reasons.append("dựa trên kinh nghiệm (Experience) thành công trong quá khứ")
        
        if features.get('ig', 0) > 0.5:
            reasons.append("cung cấp lượng tin (Information Gain) mới đáng kể cho ngữ cảnh")
            
        if features.get('concept_match_count', 0) > 0:
            reasons.append(f"có sự tương đồng cao với khái niệm Ontology '{node_key}'")

        if features.get('semantic_support_count', 0) > 0:
            reasons.append("được hỗ trợ mạnh mẽ bởi dữ liệu ngữ nghĩa (Semantic Memory)")

        narrative = f"Node '{node_key}' được chọn vì: " + ", ".join(reasons) + \
                    f". Tổng điểm đóng góp: {contribution_score:.4f}."
        
        return narrative

    def generate_trace_report(self, steps: List[Dict]) -> str:
        """Tạo báo cáo toàn bộ chuỗi lập luận phục vụ phản biện khoa học"""
        report = "--- BÁO CÁO GIẢI THÍCH CHUỖI LẬP LUẬN ---\n"
        for i, step in enumerate(steps):
            report += f"Bước {i+1}: {self.explain_selection(step['key'], step['features'], step['score'])}\n"
        report += "----------------------------------------"
        return report
