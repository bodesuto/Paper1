import logging
from typing import List, Dict, Any
import time

class SynapticLearner:
    """
    Triển khai cơ chế Synaptic Plasticity - cập nhật trọng số tri thức 
    dựa trên thành công của quá trình lập luận (Hebbian Learning).
    """
    
    def __init__(self, neo4j_driver, learning_rate: float = 0.05):
        self.driver = neo4j_driver
        self.eta = learning_rate
        self.logger = logging.getLogger("SynapticLearner")

    def update_weights(self, reasoning_path_ids: List[str], success: bool):
        """
        Cập nhật trọng số cho các quan hệ nằm trong chuỗi lập luận.
        
        Args:
            reasoning_path_ids: Danh sách các ID của mối quan hệ hoặc node tham gia.
            success: Trạng thái thành công của câu trả lời cuối cùng.
        """
        if not success:
            # Có thể triển khai Long-term Depression (LTD) ở đây nếu muốn
            return

        with self.driver.session() as session:
            # Tăng trọng số (Hebbian Potentiation)
            query = """
            UNWIND $ids AS target_id
            MATCH ()-[r {id: target_id}]-()
            SET r.synaptic_weight = coalesce(r.synaptic_weight, 1.0) + $eta,
                r.success_hits = coalesce(r.success_hits, 0) + 1,
                r.last_updated = $timestamp
            RETURN count(r) as updated_count
            """
            
            result = session.run(query, {
                "ids": reasoning_path_ids,
                "eta": self.eta,
                "timestamp": int(time.time())
            })
            
            summary = result.single()
            self.logger.info(f"Updated {summary['updated_count']} synaptic weights in Neo4j.")

    def get_highest_weighted_paths(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Lấy danh sách các 'Experience' (đường dẫn) có trọng số cao nhất"""
        query = """
        MATCH (s)-[r]->(e)
        WHERE r.synaptic_weight IS NOT NULL
        RETURN s.key as start_node, r.synaptic_weight as weight, e.key as end_node, type(r) as rel_type
        ORDER BY r.synaptic_weight DESC
        LIMIT $limit
        """
        with self.driver.session() as session:
            result = session.run(query, {"limit": limit})
            return [record.data() for record in result]
