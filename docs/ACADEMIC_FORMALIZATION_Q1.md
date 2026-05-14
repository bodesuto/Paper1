# Hình thức hóa Toán học Kiến trúc DualMemoryKG (Chuẩn Q1)

Tài liệu này cung cấp các công thức nền tảng của hệ thống, được trình bày trực quan với các từ khóa toán học bằng tiếng Anh.

---

## 1. Memory Space Definition

Hệ thống bộ nhớ kép được biểu diễn là một đồ thị tri thức hỗn hợp **G**:

**[Visible Formula]:**
> **G = (V, E)**
> Where:
> - **V (Vertices):** Includes {M_sem, M_obs, C_ont}
> - **E (Edges):** Includes {R_supp, R_conf, R_link}

**Giải thích:**
- **M_sem (Semantic Memory):** Bộ nhớ ngữ nghĩa.
- **M_obs (Observability Memory):** Bộ nhớ quan sát.
- **C_ont (Concept Ontology):** Ontology khái niệm.

**[LaTeX Code]:**
```latex
\mathcal{G} = (\mathcal{V}, \mathcal{E}) \text{ where } \mathcal{V} = \{M_{sem} \cup M_{obs} \cup C_{ont}\}
```

---

## 2. Evidence Control Optimization Objective

Hàm mục tiêu tối ưu hóa việc lựa chọn bằng chứng:

**[Visible Formula]:**
> **Utility(E) = α * Support(E) + β * Diversity(E) - γ * Redundancy(E) - δ * Contradiction(E)**

**Giải thích các thành phần:**
- **Support:** Độ hỗ trợ bằng chứng.
- **Diversity:** Tính đa dạng.
- **Redundancy:** Sự dư thừa.
- **Contradiction:** Sự mâu thuẫn.

**[LaTeX Code]:**
```latex
U(E) = \alpha \cdot \text{Supp}(E) + \beta \cdot \text{Div}(E) - \gamma \cdot \text{Red}(E) - \delta \cdot \text{Conf}(E)
```

---

## 3. Prototype Learning Mechanism

Cơ chế học nguyên mẫu để phân loại khái niệm:

**[Visible Formula]:**
> **P(c_k | x) = Exp(-dist(x, c_k)^2) / Sum[ Exp(-dist(x, c_j)^2) ]**

**Giải thích:**
- **P (Probability):** Xác suất mẫu x thuộc về khái niệm k.
- **dist (Distance):** Khoảng cách Euclidean.

**[LaTeX Code]:**
```latex
P(c_k | x) = \frac{\exp(-\|f_\phi(x) - c_k\|^2)}{\sum_j \exp(-\|f_\phi(x) - c_j\|^2)}
```

---

## 4. Lipschitz Stability

Đảm bảo tính ổn định của hệ thống trước nhiễu:

**[Visible Formula]:**
> **| Result(G_1) - Result(G_2) | ≤ K * dist(G_1, G_2)**

**Giải thích:**
- **Result:** Kết quả đầu ra của hệ thống.
- **K (Lipschitz Constant):** Hằng số ổn định Lipschitz.

**[LaTeX Code]:**
```latex
\| \mathcal{R}(G_1) - \mathcal{R}(G_2) \| \leq K \cdot d(\mathcal{G}_1, \mathcal{G}_2)
```
