# Chiến lược Tối ưu hóa DualMemoryKG (Chuẩn Q1)

Tài liệu này mô tả cách hệ thống tối ưu hóa việc học và tri thức hóa, sử dụng cách trình bày toán học trực quan Unicode và giữ nguyên các Keyword tiếng Anh.

---

## 1. Tối ưu hóa Lựa chọn Bằng chứng (Evidence Selection Optimization)

Chúng tôi sử dụng thuật toán tối ưu hóa tổ hợp để chọn tập bằng chứng **E*** tốt nhất cho mỗi câu hỏi **q**.

**[Toán học Trực quan]:**
> **E* = Điểm cao nhất của Hàm Mục Tiêu U(E)**
> Trong đó:
> **U(E) = [Lợi ích Thông tin] - [Chi phí Lưu trữ] - [Hình phạt dư thừa]**

**Các Keyword kỹ thuật:**
- **Information Gain:** Lượng thông tin bằng chứng cung cấp để giảm độ bất định (Entropy) của câu trả lời.
- **Redundancy Penalty:** Ngăn hệ thống chọn quá nhiều mẩu bằng chứng giống nhau.

---

## 2. Học tập Ontology (Ontology Learning Strategy)

Quá trình học các khái niệm suy luận (Reasoning Concepts) được thực hiện thông qua tối ưu hóa khoảng cách nguyên mẫu.

**[Toán học Trực quan]:**
> **Sai số học tập = Bình phương (Mẫu suy luận - Nguyên mẫu đại diện)**
> Mục tiêu là cực tiểu hóa tổng tất cả các sai số này.

---

## 3. Chiến lược Xác thực Căn cứ (Grounding Verification Strategy)

Hệ thống đánh giá độ tin cậy của câu trả lời dựa trên đường dẫn bằng chứng.

**[Toán học Trực quan]:**
> **Điểm Căn cứ = [Số bước có bằng chứng] / [Tổng số bước suy luận]**

**Giải thích:**
- Nếu câu trả lời có 3 bước suy luận nhưng chỉ có 2 bước tìm được bằng chứng trong bộ nhớ, **Điểm Căn cứ** sẽ là **67%**. Bài báo Q1 yêu cầu chỉ số này phải đạt mức cao (>90%).

---
**Mã LaTeX để copy:**
```latex
\min_{\theta} \sum_{i=1}^n \| f_\theta(x_i) - c_{y_i} \|^2
\mathcal{G}_{score} = \frac{|P_{verified}|}{|P_{total}|}
```
