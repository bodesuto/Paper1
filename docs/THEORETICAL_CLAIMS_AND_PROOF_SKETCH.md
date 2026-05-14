# Các Tuyên bố Lý thuyết và Phác thảo Chứng minh (Chuẩn Q1)

---

## Claim 1: Lipschitz Stability of Grounded Reasoning

**[Visible Formula]:**
> **| Output(G_new) - Output(G_old) | ≤ K * dist(G_new, G_old)**

**Lập luận:**
- Mọi thay đổi trong câu trả lời đều bị giới hạn bởi sự thay đổi trong bộ nhớ. Hằng số **K** nhỏ đảm bảo tính ổn định vững chắc cho hệ thống.

---

## Claim 2: Error Bound of Ontology Induction

**[Visible Formula]:**
> **Error(Ontology) = O( Complexity / sqrt(N_samples) )**

**Lập luận:**
- Khi số lượng vết suy luận (**N_samples**) tiến tới vô hạn, sai số phân loại khái niệm sẽ hội tụ về 0.

---

## Claim 3: Optimal Information Gain in Evidence Selection

**[Visible Formula]:**
> **Selection(E*) = Argmax[ Information_Gain(E) / Cost(E) ]**

**Lập luận:**
- Chiến lược tham lam đảm bảo hệ thống chọn được những bằng chứng "đắt giá" nhất về mặt thông tin trên mỗi đơn vị chi phí.

---

## Claim 4: Domain Independence via Functional Abstraction

**[Visible Formula]:**
> **Logic(Grounding) ⊥ Semantics(Domain)**

**Lập luận:**
- Quy trình xác thực và lựa chọn bằng chứng mang tính cấu trúc và đồ thị, do đó nó độc lập (⊥) với nội dung ngôn ngữ cụ thể của lĩnh vực.

---

**LaTeX Proof References:**
```latex
\lim_{n \to \infty} P(\| \hat{c} - c^* \| > \epsilon) = 0
\Delta y \leq K \cdot \Delta \mathcal{G}
```
