# Chiến lược Đối chứng SOTA và Lựa chọn Dataset (Chuẩn Q1)

Tài liệu này định hình cách DualMemoryKG khẳng định vị thế học thuật thông qua việc so sánh với các đối thủ mạnh nhất và sử dụng các tập dữ liệu cực kỳ khắt khe.

---

## 1. Các Đối thủ so sánh (SOTA Baselines)

Để bài báo đạt chuẩn Q1, chúng ta phải đối đầu trực diện với:

1.  **Vanilla RAG / Vector-RAG:** Hệ thống truy xuất tương đồng đơn giản (Baseline thấp nhất).
2.  **GraphRAG (Microsoft):** Hệ thống truy xuất dựa trên đồ thị tri thức tĩnh.
3.  **Self-RAG:** Hệ thống có khả năng tự phản hồi nhưng chưa có bộ nhớ quan sát (Observability).
4.  **ReAct / Reflexion (Trực tiếp):** Các tác tử suy luận không có sự hỗ trợ của bộ nhớ kép.

---

## 2. Lựa chọn Tập dữ liệu (Dataset Strategy)

Chúng ta không chọn các tập dữ liệu dễ. Chúng ta chọn các tập dữ liệu có tính "Thách thức suy luận":

*   **HotpotQA:** Yêu cầu suy luận đa bước (Multi-hop). DualMemoryKG sẽ thắng nhờ khả năng kết nối các nút trong đồ thị.
*   **MuSiQue:** Độ phức tạp cao hơn HotpotQA, yêu cầu các chuỗi suy luận dài.
*   **HaluEval:** Tập dữ liệu chuyên biệt để đánh giá Ảo giác (Hallucination). Đây là nơi chúng ta thể hiện sức mạnh của **Lipschitz Stability**.

---

## 3. Chỉ số Đánh giá (Evaluation Metrics)

Ngoài các chỉ số truyền thống (F1, Exact Match), chúng ta giới thiệu các chỉ số chuyên sâu:

**[Visible Formula]:**
> **Grounding_Precision = Verified_Evidence_Nodes / Total_Retrieved_Nodes**
> **Reasoning_Efficiency = Answer_Accuracy / Token_Cost**

---

## 4. Insight về Khả năng Chống nhiễu (Robustness Insight)

Một thí nghiệm then chốt cho bài báo Q1 là **Stress Test**:
- Chúng ta sẽ tiêm "Bằng chứng giả" (Distractors) vào bộ nhớ.
- **Dự đoán:** DualMemoryKG sẽ ổn định hơn các hệ thống RAG khác nhờ hàm mục tiêu lọc mâu thuẫn (**Contradiction Penalty**).

---
**Mã LaTeX cho bảng kết quả dự kiến:**
```latex
\text{Improvement} = \frac{\text{Score}_{\text{DualMemory}} - \text{Score}_{\text{SOTA}}}{\text{Score}_{\text{SOTA}}} \times 100\%
```
