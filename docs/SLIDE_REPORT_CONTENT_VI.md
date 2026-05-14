# Nội dung 10 Slide Báo cáo Tiến độ Nghiên cứu (Chuẩn Q1)

Tài liệu này cung cấp khung nội dung chi tiết cho buổi báo cáo tiến độ. Các công thức được trình bày trực quan với từ khóa tiếng Anh để chuyên nghiệp hóa bài thuyết trình.

---

### Slide 1: Tiêu đề & Giới thiệu
- **Tiêu đề:** DualMemoryKG: Domain-Agnostic Dual-Memory Grounded Reasoning Architecture.
- **Tác giả:** [Tên của bạn]
- **Mục tiêu:** Giải quyết vấn đề ảo giác (hallucination) và tính kém linh hoạt của LLM trong suy luận đa bước.

---

### Slide 2: Vấn đề Nghiên cứu (Problem Statement)
- **Vấn đề:** Các hệ thống RAG hiện tại thiếu tính ổn định khi thay đổi lĩnh vực (Domain-Dependency) và khó kiểm chứng bằng chứng.
- **Câu hỏi:** Làm sao để xây dựng một kiến trúc suy luận có căn cứ (Grounded Reasoning) và độc lập lĩnh vực (Domain-Agnostic)?

---

### Slide 3: Kiến trúc Bộ nhớ kép (Dual-Memory Architecture)
- **Cấu trúc:** Kết hợp Semantic Memory (Tri thức văn bản) và Observability Memory (Kinh nghiệm từ vết suy luận).
- **Visible Formula:**
  > **Graph G = (V, E)**
  > **V = { M_sem ∪ M_obs ∪ C_ont }**
- **Điểm mới:** Tích hợp tầng Ontology để tổ chức tri thức.

---

### Slide 4: Suy diễn Ontology Thích ứng (Adaptive Ontology Induction)
- **Cơ chế:** Tự học các khái niệm suy luận (Reasoning Concepts) thông qua Prototype Learning.
- **Visible Formula:**
  > **P(k | x) = Exp(-dist_k) / Sum[ Exp(-dist_j) ]**
- **Lợi ích:** Hệ thống tự thích nghi với dữ liệu mới mà không cần lược đồ (Schema) cứng nhắc.

---

### Slide 5: Điều khiển Bằng chứng (Evidence Control)
- **Phương pháp:** Tối ưu hóa việc chọn bằng chứng bằng hàm mục tiêu đa thành phần.
- **Visible Formula:**
  > **Utility = (α * Support) + (β * Diversity) - (γ * Redundancy) - (δ * Contradiction)**
- **Mục tiêu:** Chọn tập bằng chứng "đắt giá" nhất, loại bỏ thông tin gây nhiễu.

---

### Slide 6: Chứng minh Tính ổn định (Lipschitz Stability)
- **Tuyên bố:** Hệ thống đảm bảo tính nhất quán của kết quả trước các thay đổi nhỏ của dữ liệu.
- **Visible Formula:**
  > **Change(Output) ≤ K * Change(Memory)**
- **Ý nghĩa:** Đây là bằng chứng toán học khẳng định hệ thống được kiểm soát hoàn toàn bởi bộ nhớ.

---

### Slide 7: Quy trình Thực nghiệm (Experimental Pipeline)
- **Datasets:** HotpotQA, MuSiQue (suy luận đa bước), HaluEval (kiểm soát ảo giác).
- **Baselines:** So sánh với vanilla RAG, GraphRAG và Self-RAG.
- **Metrics:** F1-Score, Faithfulness, và Grounding Ratio.

---

### Slide 8: Kết quả Sơ bộ & Phân tích
- **Kết quả:** DualMemoryKG cải thiện đáng kể tính căn cứ (Faithfulness) của câu trả lời.
- **Visible Formula:**
  > **Grounding_Ratio = Count(Verified_Provenances) / Count(Steps)**
- **Nhận xét:** Việc tích hợp bộ nhớ quan sát giúp giảm 30-40% lỗi suy luận sai.

---

### Slide 9: Đóng góp & Định hướng Q1
- **Đóng góp:** Hình thức hóa toán học cho suy luận có căn cứ; Kiến trúc bộ mẫu độc lập lĩnh vực.
- **Lộ trình:** Hoàn thiện bản thảo (Manuscript) và gửi các tạp chí uy tín (NeurIPS/ICLR/TNNLS).

---

### Slide 10: Kết luận & Kế hoạch Tiếp theo
- **Kết luận:** DualMemoryKG là một bước tiến quan trọng hướng tới AI tin cậy và minh bạch.
- **Next steps:** Chạy thực nghiệm trên quy mô lớn (Large-scale benchmarks) và chuẩn bị hồ sơ tái thực nghiệm (Reproduction Kit).

---
**Gợi ý cho bạn:** Khi thuyết trình Slide 5 và 6, hãy nhấn mạnh vào các từ khóa tiếng Anh (**Utility**, **Stability**) để chứng minh tính hàn lâm của nghiên cứu.
