# Tổng hợp bài báo Q1: Hệ cấp Suy luận có Căn cứ (DualMemoryKG)

Bản tổng hợp này thiết lập cấu trúc logic "4 tầng" (The Stack) để giải quyết triệt để bài toán suy luận tin cậy trong các hệ thống LLM.

---

## 1. ABSTRACT (Tóm tắt luận điểm)
Bài báo đề xuất DualMemoryKG, một kiến trúc suy luận có căn cứ đột phá dựa trên nguyên lý điều khiển tri thức. Thay vì tập trung vào cải tiến truy xuất (Retrieval), chúng tôi tập trung vào việc **Quản trị nhận thức của tác tử** thông qua 4 lớp đóng góp: Lưu trữ bộ nhớ kép (C1), Suy diễn Ontology thích ứng (C2), Điều khiển bằng chứng (C3), và Xác thực ổn định (C4).

---

## 2. THE GROUNDED REASONING STACK (Cấu trúc đóng góp)

### Tầng 1: Unified Storage (C1 - Đóng góp thực thể)
- **Tuyên bố:** Suy luận đa bước đòi hỏi cả tri thức văn bản và nhật ký kinh nghiệm.
- **Giải pháp:** Lược đồ đồ thị tri thức tích hợp `SemanticMemory` ⊕ `ObservabilityMemory`.

### Tầng 2: Cognitive Perception (C2 - Đóng góp nhận thức)
- **Tuyên bố:** Tác tử phải tự nhận diện được mẫu suy luận từ dữ liệu thô.
- **Giải pháp:** Cơ chế **Adaptive Ontology Induction** dựa trên Prototype Learning.
- **Visible Formula:** `P(k|x) = Softmax(-dist(x, c_k))`

### Tầng 3: Knowledge Control (C3 - Đóng góp tối ưu)
- **Tuyên bố:** Việc nạp bằng chứng phải tuân theo luật tối ưu hóa thông tin, không phải độ tương đồng bề mặt.
- **Giải pháp:** Thuật toán lựa chọn dựa trên **Information Gain vs. Redundancy**.

### Tầng 4: Safety Verification (C4 - Đóng góp kiểm chứng)
- **Tuyên bố:** Độ tin cậy phải được chứng minh bằng toán học, không chỉ bằng cảm tính.
- **Giải pháp:** Chứng minh tính ổn định Lipschitz cho hệ thống.
- **Visible Formula:** `|| Δ_Output || ≤ K * || Δ_Evidence ||`

---

## 3. RESULTS & IMPACT (Kết quả và Tác động)
- **Benchmark:** Hiệu năng vượt trội trên HotpotQA và MuSiQue nhờ khả năng kiểm soát đường dẫn suy luận.
- **Insight:** DualMemoryKG không bị đánh lừa bởi các bằng chứng gây nhiễu (Distractors) nhờ tầng lọc C3 và C4.

---
**Kết luận:** Sự kết nối chặt chẽ giữa 4 tầng này tạo nên một hệ thống suy luận không chỉ mạnh mẽ mà còn có thể giải thích (Explainable) và có căn cứ (Grounded).
