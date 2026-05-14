# Hình thức hóa Toán học Kiến trúc DualMemoryKG (Chuẩn Q1)

Tài liệu này cung cấp các công thức nền tảng của hệ thống, được trình bày theo cách trực quan để dễ dàng đọc hiểu mà không cần bộ lọc toán học chuyên dụng.

---

## 1. Định nghĩa Không gian Bộ nhớ (Memory Space)

Hệ thống bộ nhớ kép được biểu diễn là một đồ thị tri thức hỗn hợp **G**:

**[Công thức trực quan]:**
> **G = (V, E)**
> Trong đó:
> - **V (Vertices/Nút):** Bao gồm {M_sem, M_obs, C_ont}
> - **E (Edges/Cạnh):** Bao gồm {R_supp, R_conf, R_link}

**Giải thích chi tiết:**
- **M_sem (Semantic Memory):** Các thực thể và quan hệ từ văn bản (ví dụ: "Thủ đô của Pháp là Paris").
- **M_obs (Observability Memory):** Dữ liệu từ vết suy luận và nhật ký lỗi (ví dụ: "Tác tử đã trả lời sai ở bước 2").
- **C_cont (Concept Ontology):** Các khái niệm suy luận trừu tượng được học từ dữ liệu.
- **R_supp / R_conf / R_link:** Các quan hệ Hỗ trợ (Support), Mâu thuẫn (Conflict) và Liên kết (Link).

**[Mã LaTeX để copy vào bài báo]:**
```latex
\mathcal{G} = (\mathcal{V}, \mathcal{E}) \text{ where } \mathcal{V} = \{M_{sem} \cup M_{obs} \cup C_{ont}\}
```

---

## 2. Mục tiêu Tối ưu hóa Điều khiển Bằng chứng (Evidence Control)

Khi hệ thống lựa chọn bằng chứng (E), nó không chỉ dựa trên độ tương đồng mà dựa trên hàm mục tiêu **U(E)**:

**[Công thức trực quan]:**
> **U(E) = α * Support(E) + β * Diversity(E) - γ * Redundancy(E) - δ * Contradiction(E)**

**Giải thích các Keyword:**
- **Support (Hỗ trợ):** Mức độ bằng chứng giải thích được cho câu hỏi.
- **Diversity (Đa dạng):** Sự khác biệt giữa các nguồn bằng chứng (tránh bị lệch một phía).
- **Redundancy (Dư thừa):** Trừ bớt điểm nếu các bằng chứng trùng lặp nội dung.
- **Contradiction (Mâu thuẫn):** Phạt nặng nếu bằng chứng tự mâu thuẫn lẫn nhau.
- **α, β, γ, δ:** Các trọng số điều chỉnh mức độ ưu tiên.

**[Mã LaTeX để copy vào bài báo]:**
```latex
U(E) = \alpha \cdot \text{Supp}(E) + \beta \cdot \text{Div}(E) - \gamma \cdot \text{Red}(E) - \delta \cdot \text{Conf}(E)
```

---

## 3. Cơ chế Học Nguyên mẫu (Prototype Learning)

Để phân loại các khái niệm trong Ontology, chúng tôi sử dụng khoảng cách Euclidean đến các nguyên mẫu **c_k**:

**[Công thức trực quan]:**
> **Xác suất (Khái niệm k | x) = Exp(-Khoảng cách(x, c_k)) / Tổng[Exp(-Khoảng cách(x, c_j))]**

**Giải thích chi tiết:**
- **x:** Vector biểu diễn (Embedding) của một mẫu suy luận mới.
- **c_k:** Điểm trung tâm (Prototype) của khái niệm thứ **k**.
- Công thức này đảm bảo rằng mẫu **x** càng gần nguyên mẫu nào thì xác suất thuộc về khái niệm đó càng cao.

**[Mã LaTeX để copy vào bài báo]:**
```latex
P(c_k | x) = \frac{\exp(-\|f_\phi(x) - c_k\|^2)}{\sum_j \exp(-\|f_\phi(x) - c_j\|^2)}
```

---

## 4. Tính ổn định Lipschitz (Lipschitz Stability)

Để đảm bảo hệ thống không bị thay đổi câu trả lời quá lớn khi dữ liệu bộ nhớ bị nhiễu nhẹ:

**[Công thức trực quan]:**
> **|Kết quả(G_1) - Kết quả(G_2)| ≤ K * |G_1 - G_2|**

**Giải thích:**
- **K (Lipschitz Constant):** Nếu **K** nhỏ, hệ thống cực kỳ ổn định.
- Điều này chứng minh rằng DualMemoryKG có khả năng chống nhiễu (Robustness) tốt hơn các hệ thống RAG thông thường.

**[Mã LaTeX để copy vào bài báo]:**
```latex
\| \mathcal{R}(G_1) - \mathcal{R}(G_2) \| \leq K \cdot d(\mathcal{G}_1, \mathcal{G}_2)
```

---
**Ghi chú:** Toàn bộ các công thức trên đã được đơn giản hóa để hiển thị tốt trên mọi trình soạn thảo văn bản. Đối với các bản thảo gửi tạp chí, hãy sử dụng mã LaTeX trong các khối code tương ứng.
