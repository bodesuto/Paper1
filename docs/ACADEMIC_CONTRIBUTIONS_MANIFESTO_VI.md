# Tuyên ngôn Đóng góp Khoa học của DualMemoryKG (Chuẩn Q1)

Tài liệu này tóm tắt các giá trị khoa học cốt lõi của dự án, được trình bày với các công thức toán học trực quan để phục vụ báo cáo và phản biện chuyên gia.

---

## 1. Đột phá 1: Suy diễn Ontology Thích ứng (Adaptive Ontology Induction)

Thay vì sử dụng các nhãn cố định (heuristics), DualMemoryKG tự học các khái niệm suy luận trực tiếp từ dữ liệu.

**[Mô tả Toán học Trực quan]:**
> **Xác suất (Khái niệm k | Hành động x) ≈ Độ gần của x với tâm khái niệm c_k**
> Sử dụng hàm Softmax để chuẩn hóa:
> **P = Exp(-d_k) / Tổng[Exp(-d_j)]**

**Ý nghĩa Khoa học:**
- Cho phép hệ thống tự thích nghi với các lĩnh vực mới mà không cần chuyên gia gán nhãn thủ công (Domain-Agnostic).

---

## 2. Đột phá 2: Điều khiển Bằng chứng dựa trên Lý thuyết Thông tin

Việc lựa chọn bằng chứng được tối ưu hóa để tối đa hóa lượng thông tin thu được (**Information Gain**) đồng thời giảm thiểu sự dư thừa.

**[Mô tả Toán học Trực quan]:**
> **Mục tiêu tối ưu = [Thông tin mới nhận được] - [Thông tin dư thừa] - [Độ phức tạp tính toán]**

**Giải thích các Keyword:**
- **Information Gain:** Lượng tri thức mới mà bằng chứng cung cấp cho câu hỏi.
- **Redundancy Penalty:** Hình phạt cho việc lấy các bằng chứng lặp lại thông tin đã có.

---

## 3. Đột phá 3: Đảm bảo Tính ổn định vững chắc (Lipschitz Continuity)

Chúng tôi chứng minh về mặt toán học rằng hệ thống phản ứng ổn định trước các biến động nhỏ của bộ nhớ (nhiễu dữ liệu).

**[Mô tả Toán học Trực quan]:**
> **Biến động Đầu ra ≤ Hệ số ổn định (K) * Biến động Bộ nhớ**

**Ý nghĩa Khoa học:**
- Đây là bằng chứng toán học quan trọng để bảo vệ bài báo trước các câu hỏi về "Hallucination" (Ảo giác) của LLM. Một giá trị **K** thấp chứng minh rằng hệ thống được kiểm soát chặt chẽ bởi bằng chứng trong bộ nhớ.

---

## 4. Tóm tắt Đóng góp cho Cộng đồng (Academic Contributions)

1.  **Framework mới:** Kiến trúc Bộ nhớ kép (Semantic + Observability) đầu tiên có tích hợp tầng Ontology thích ứng.
2.  **Độ tin cậy cao:** Giảm tỷ lệ suy luận không căn cứ (unsupported reasoning) xuống mức tối thiểu thông qua tầng xác thực (Verification Layer).
3.  **Khả năng tái sử dụng:** Chứng minh tính hiệu quả trên nhiều tập dữ liệu chuẩn (HotpotQA, MuSiQue, HaluEval).

---
**Mã LaTeX chuyên sâu:** (Nếu bạn cần copy vào tệp .tex của bài báo)
```latex
% Lipschitz Stability Claim
\| \mathcal{R}(G \cup \{e\}) - \mathcal{R}(G) \| \leq K \cdot \text{Surprisal}(e)

% Evidence Utility Objective
\mathcal{U}(E) = I(y; E | q) - \lambda \cdot \text{Cost}(E)
```
