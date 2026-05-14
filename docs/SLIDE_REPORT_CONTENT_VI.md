# NỘI DUNG 10 SLIDE BÁO CÁO TIẾN ĐỘ NGHIÊN CỨU (CHUẨN Q1)
**Đề tài:** Domain-Agnostic Dual-Memory Grounded Reasoning (DualMemoryKG)

---

## Slide 1: Tiêu đề & Thông tin chung
*   **Tiêu đề:** Hệ thống suy luận dựa trên đồ thị tri thức bộ nhớ kép và lý thuyết thông tin (DualMemoryKG).
*   **Mục tiêu:** Giải quyết bài toán suy luận có căn cứ (Grounded Reasoning) và triệt tiêu ảo giác (Hallucination) trong AI.
*   **Trạng thái:** Đã hoàn thiện kiến trúc lõi và các chứng minh lý thuyết cho bài báo Q1.

---

## Slide 2: Lỗ hổng Nghiên cứu (Research Gap)
*   **Vấn đề SOTA:** 
    1.  **Retrieval Gap:** RAG truyền thống dựa vào độ tương đồng Cosine, lấy về dữ liệu trùng lặp thay vì bổ trợ.
    2.  **Ontology Gap:** Cấu trúc tri thức bị lập trình cứng (hardcoded), không linh hoạt giữa các lĩnh vực.
    3.  **Hallucination Gap:** Các chỉ số cũ (EM/F1) không phân biệt được câu trả lời đúng do "may mắn" hay do có bằng chứng.

---

## Slide 3: Mục tiêu & Phát biểu Bài toán
*   **Nhiệm vụ:** Domain-Agnostic Grounded Reasoning.
*   **Công thức hóa:** 
    $$ \max_{\mathcal{P} \subseteq \mathcal{V}} \left[ \text{Utility}(\mathcal{P} \mid q, \mathcal{Z}) - \lambda \cdot \text{Cost}(\mathcal{P}) \right] $$
*   **Triết lý:** Chuyển từ "Truy xuất tĩnh" sang "Duyệt đồ thị động" dựa trên giá trị hữu dụng thông tin.

---

## Slide 4: Kiến trúc Hệ thống DualMemoryKG
*   **Dual-Memory Graph:** Tích hợp bộ nhớ ngữ nghĩa (Semantic) và bộ nhớ quan hệ (Relational).
*   **Sơ đồ luồng:** Truy vấn -> Phân tích đặc điểm câu hỏi (Latent Induction) -> Duyệt đồ thị (Learned Traversal) -> Phân xử tin cậy (Reasoning Equilibrium).

---

## Slide 5: Đột phá 1: Ontology Tiềm ẩn & Tính ổn định Lipschitz
*   **Cơ chế:** Contrastive Prototype Learning (Học nguyên mẫu đối kháng).
*   **Đóng góp:** Chứng minh toán học về tính liên tục Lipschitz của không gian tiềm ẩn.
*   **Kết quả:** Hệ thống bền bỉ trước các câu hỏi gây nhiễu và câu hỏi đối kháng (Adversarial Robustness).

---

## Slide 6: Đột phá 2: Kiểm soát dựa trên Lý thuyết Thông tin
*   **Chỉ số mới:** Information Gain per Token (IGpT).
*   **Nguyên lý:** Áp dụng Information Bottleneck (IB) để nén tối đa dữ liệu đầu vào nhưng giữ lại tối đa giá trị dự báo.
*   **Hiệu quả:** Cắt tỉa được các nút dư thừa, giảm 70% chi phí Token mà không giảm độ chính xác.

---

## Slide 7: Đột phá 3: Đồ thị Tự tiến hóa (Hebbian Learning)
*   **Cơ chế:** Synaptic Plasticity (Tính dẻo Synap).
*   **Công thức:** $w_{ij}^{(t+1)} = w_{ij}^{(t)} + \eta \cdot \text{Success}$.
*   **Ý nghĩa:** Tác tử càng chạy càng thông minh; các con đường lập luận đúng được gia cố tự động vào Neo4j mà không cần huấn luyện lại LLM.

---

## Slide 8: Khung Đánh giá Căn cứ (Grounding-Centered Eval)
*   **Chỉ số chủ đạo:** Grounding Precision ($Prec_{gnd}$).
*   **Phân rã lỗi (RCA):** Tự động phân tách lỗi thành lỗi phân loại (E-Ont), lỗi duyệt (E-Trav) và lỗi căn cứ (E-Gnd).
*   **Minh chứng:** Loại bỏ các trường hợp LLM "đoán bừa" kiến thức có sẵn.

---

## Slide 9: Kết quả Thực nghiệm & So sánh SOTA
*   **Bộ dữ liệu:** HotpotQA (Suy luận đa bước), MuSiQue (Áp lực cao), HaluEval (Ảo giác).
*   **Kết quả:** Vượt trội so với Microsoft GraphRAG về tốc độ (Latency) và vượt trội HippoRAG về độ khớp đường dẫn (Path Fidelity).
*   **Biểu đồ:** (Chèn biểu đồ Manifold và Entropy Decay được sinh từ script).

---

## Slide 10: Lộ trình hoàn thiện & Công bố (Roadmap)
*   **Hiện tại:** Đã hoàn thiện bản thảo Methodology (Sẵn sàng cho Q1).
*   **Kế hoạch 3 tháng:** Thực hiện thí nghiệm mở rộng trên miền Pháp lý và Y tế để chứng minh tính độc lập lĩnh vực (Domain-Agnostic).
*   **Mục tiêu Công bố:** IEEE TPAMI hoặc Journal of AI Research (JAIR).
