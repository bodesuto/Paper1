# Tổng hợp Bài báo Nghiên cứu DualMemoryKG (Chuẩn Q1)

---

## 1. System Architecture

### 1.1. Universal Typed Memory
**[Visible Formula]:**
- **Graph G = (V, E)**
- **V = { M_sem, M_obs, C_ont }**

### 1.2. Adaptive Ontology Induction
**[Visible Formula]:**
- **P(k|x) = Exp(-dist_k) / Sum[ Exp(-dist_j) ]**

---

## 2. Methodology & Optimization

**[Visible Formula]:**
> **Utility_Score = (w1 * Support) + (w2 * Diversity) - (w3 * Redundancy) - (w4 * Contradiction)**

---

## 3. Core Theoretical Claims

1.  **Lipschitz Stability:** Output remains stable under memory noise.
2.  **Convergence:** Ontology prototypes improve with more trace data.
3.  **Faithfulness:** Every answer is derived from a verifiable path **P ⊆ G**.

---

## 4. Experimental Targets

**[Visible Formula]:**
- **F1_Score = 2 * (Precision * Recall) / (Precision + Recall)**
- **Grounding_Ratio = Verified_Steps / Total_Steps**

---
**LaTeX Snips:**
```latex
\mathcal{U}(E) = \sum_{i} \omega_i \cdot \phi_i(E)
\mathcal{R} : \mathcal{G} \to \mathcal{Y}
```
