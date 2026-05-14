# Hình thức hóa Toán học: The Grounded Reasoning Stack (DualMemoryKG)

Tài liệu này hệ thống hóa các nền tảng toán học của hệ thống theo 4 lớp đóng góp khoa học kế thừa.

---

## Lớp 1: Cấu trúc Bộ nhớ Hỗn hợp (Storage Layer)

**Mục tiêu:** Định nghĩa không gian tri thức tích hợp.

**[Visible Formula]:**
> **G = (V, E)**
> **V = { M_semantic, M_observability, C_ontology }**

**Giải thích:** Đồ thị tri thức **G** là sự hợp nhất giữa dữ liệu tĩnh và nhật ký thực thi thực tế.

---

## Lớp 2: Suy diễn Nhận thức (Perception Layer)

**Mục tiêu:** Tự động nhận diện cấu trúc suy luận từ kinh nghiệm.

**[Visible Formula]:**
> **P(c_k | x) = Exp(-dist(x, c_k)^2) / Sum[ Exp(-dist(x, c_j)^2) ]**

**Giải thích:** Xác suất mẫu **x** thuộc về khái niệm **c_k** được tính dựa trên khoảng cách Euclidean trong không gian embedding.

---

## Lớp 3: Điều khiển tri thức tối ưu (Control Layer)

**Mục tiêu:** Lựa chọn bộ bằng chứng tối ưu cho suy luận.

**[Visible Formula]:**
> **Utility(E) = α * Information_Gain(E) - β * Redundancy(E)**

**Giải thích:** Việc chọn bằng chứng được mô hình hóa như một bài toán tối ưu hóa thông tin, cân bằng giữa lượng tin thu được và sự lặp lại.

---

## Lớp 4: Xác thực ổn định (Verification Layer)

**Mục tiêu:** Chứng minh tính tin cậy của hệ thống.

**[Visible Formula]:**
> **|| Δ_Output || ≤ K * || Δ_Evidence ||**

**Giải thích:** Định lý Lipschitz đảm bảo rằng sai số của câu trả lời được kiểm soát chặt chẽ bởi chất lượng của bằng chứng nạp vào, ngăn chặn ảo giác ngẫu nhiên.

---
**Kết luận:** Sự mạch lạc toán học nằm ở việc kết quả của Lớp 1 là đầu vào của Lớp 2, Lớp 2 cung cấp ngữ cảnh cho Lớp 3, và Lớp 4 bảo chứng cho toàn bộ quy trình.
