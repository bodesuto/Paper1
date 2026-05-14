# Tổng hợp Bài báo Nghiên cứu DualMemoryKG (Chuẩn Q1)

Tài liệu này tổng hợp toàn bộ các thành phần của bài báo, từ kiến trúc đến thực nghiệm, được trình bày với định dạng toán học trực quan và giữ nguyên các Keyword chuyên môn.

---

## 1. Kiến trúc Hệ thống (System Architecture)

DualMemoryKG vận hành dựa trên sự phối hợp của 4 lớp chính:

### 1.1. Lớp Bộ nhớ có Kiểu (Universal Typed Memory)
Hợp nhất bằng chứng từ văn bản và kinh nghiệm từ vết suy luận.
**[Toán học Trực quan]:**
- **Đồ thị G = (V, E)**
- **Nút V:** {Dữ liệu ngữ nghĩa, Nhật ký quan sát, Khái niệm Ontology}

### 1.2. Lớp Suy diễn Ontology (Adaptive Ontology Induction)
Tự học các mẫu suy luận từ dữ liệu.
**[Toán học Trực quan]:**
- **Xác suất phân loại = Exp(-Khoảng cách) / Tổng[Exp(-Khoảng cách)]**

---

## 2. Phương pháp luận (Methodology)

Chúng tôi tối ưu hóa quá trình suy luận thông qua **Hàm Mục tiêu Điều khiển Bằng chứng (Evidence Control Objective)**:

**[Toán học Trực quan]:**
> **Điểm ưu tiên = (Trọng số 1 * Độ hỗ trợ) + (Trọng số 2 * Tính đa dạng) - (Trọng số 3 * Sự dư thừa) - (Trọng số 4 * Mâu thuẫn)**

**Tại sao lại dùng công thức này?**
- Để đảm bảo LLM nhận được đủ bằng chứng (Hỗ trợ) nhưng không bị rối bởi thông tin lặp lại (Dư thừa) hoặc thông tin gây nhiễu (Mâu thuẫn).

---

## 3. Các Tuyên bố Khoa học (Theoretical Claims)

1.  **Tính ổn định (Stability):** Kết quả suy luận không đổi đột ngột khi bộ nhớ có nhiễu nhẹ.
2.  **Tính hội tụ (Convergence):** Các khái niệm tự học sẽ ngày càng chính xác hơn theo thời gian.
3.  **Tính căn cứ (Faithfulness):** 100% các câu trả lời đều có đường dẫn bằng chứng đi kèm (Evidence Provenance).

---

## 4. Kết quả Thực nghiệm (Experimental Results)

**Số liệu mục tiêu (Target Benchmarks):**
- **HotpotQA:** Đạt độ chính xác (F1) vượt trội so với vanilla RAG nhờ khả năng suy luận đa bước (Multi-hop).
- **HaluEval:** Giảm tỷ lệ ảo giác (Hallucination) đáng kể nhờ tầng xác thực bằng chứng.

---
**Copy mã LaTeX tại đây:**
```latex
% System Objective
\arg \max_{E \in \mathcal{G}} \mathcal{U}(E)

% Faithfulness Constraint
\forall y, \exists P \subseteq \mathcal{G} : P \vdash y
```
