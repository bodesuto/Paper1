# Các Tuyên bố Lý thuyết và Phác thảo Chứng minh (Chuẩn Q1)

Tài liệu này trình bày nền tảng lý thuyết của DualMemoryKG dưới dạng các tuyên bố khoa học (Claims) và các lập luận logic để bảo vệ các tuyên bố đó.

---

## Tuyên bố 1: Tính ổn định Lipschitz của Hệ thống Suy luận

**[Phát biểu trực quan]:**
> Khi chúng ta thêm hoặc bớt một đơn vị bằng chứng nhỏ vào bộ nhớ, kết quả suy luận của hệ thống sẽ **không bao giờ thay đổi đột ngột hoặc mất kiểm soát**. Sự thay đổi của kết quả luôn nhỏ hơn hoặc bằng một hằng số **K** nhân với độ quan trọng của bằng chứng đó.

**Tại sao điều này quan trọng?**
- Nó chứng minh hệ thống không bị "ảo giác" (hallucination) ngẫu nhiên. Mọi thay đổi trong câu trả lời đều phải có lý do từ sự thay đổi trong bộ nhớ.

**Phác thảo chứng minh:**
1. Chúng tôi mô hình hóa quá trình chọn bằng chứng như một hàm xác suất trên đồ thị.
2. Bằng cách sử dụng các hàm kích hoạt (như Softmax) có đạo hàm bị chặn, chúng tôi giới hạn được tốc độ thay đổi của xác suất chọn bằng chứng.
3. Kết quả là hàm suy luận tổng thể trở nên liên tục và ổn định (Lipschitz continuous).

---

## Tuyên bố 2: Ranh giới Sai số của Suy diễn Ontology

**[Phát biểu trực quan]:**
> Sai số khi hệ thống tự học các khái niệm (Ontology) sẽ giảm dần khi số lượng vết suy luận (traces) trong bộ nhớ quan sát tăng lên. Sai số này bị chặn bởi một giá trị phụ thuộc vào **Độ phức tạp của dữ liệu** và **Số lượng mẫu huấn luyện**.

**Ý nghĩa:**
- Hệ thống càng hoạt động lâu, khả năng hiểu các khái niệm suy luận của nó càng chính xác (cơ chế tự học - Self-learning).

**Phác thảo chứng minh:**
1. Sử dụng lý thuyết học máy thống kê về tính nhất quán của phương pháp phân cụm nguyên mẫu (Prototype-based clustering).
2. Chứng minh rằng các tâm nguyên mẫu (c_k) sẽ hội tụ về cấu trúc suy luận thực tế của bài toán khi số lượng mẫu tiến tới vô hạn.

---

## Tuyên bố 3: Tối ưu hóa thu nhận thông tin (Optimal Information Gain)

**[Phát biểu trực quan]:**
> Chiến lược lựa chọn bằng chứng của chúng tôi đạt được sự cân bằng tối ưu giữa **Độ bao phủ câu hỏi** và **Chi phí tính toán**. Chúng tôi không lấy dư thừa bằng chứng nhưng cũng không bỏ sót bằng chứng quan trọng.

**Mô tả logic:**
- Hệ thống sử dụng thuật toán Tham lam (Greedy) để chọn ra những mẩu bằng chứng có "giá trị thông tin trên mỗi đơn vị chi phí" là cao nhất.

---

## Tuyên bố 4: Tính độc lập lĩnh vực (Domain Independence)

**[Phát biểu trực quan]:**
> Kiến trúc DualMemoryKG có thể chuyển đổi sang các lĩnh vực mới (như từ Luật sang Y tế) mà không cần thay đổi thuật toán cốt lõi. Chỉ cần thay đổi lớp Giao diện (Adapter).

**Phác thảo chứng minh:**
1. Các thành phần logic như "Xác thực bằng chứng" và "Lựa chọn dựa trên mâu thuẫn" được định nghĩa dựa trên các thuộc tính toán học của đồ thị, không phụ thuộc vào ý nghĩa ngôn ngữ cụ thể.
2. Kết quả thí nghiệm trên các tập dữ liệu khác nhau (HotpotQA, MuSiQue) cho thấy sự ổn định về hiệu năng.

---

**Khối mã LaTeX cho các chứng minh chính thức:**
```latex
% Claim 1: Lipschitz Stability
\Delta \text{Output} \leq K \cdot \Delta \text{Memory}

% Claim 2: Convergence of Prototypes
\lim_{n \to \infty} \| \hat{c}_k - c_k^* \| = 0
```
