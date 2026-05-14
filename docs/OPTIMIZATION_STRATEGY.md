# Chiến lược Tối ưu hóa DualMemoryKG (Chuẩn Q1)

---

## 1. Evidence Selection Optimization

**[Visible Formula]:**
> **Optimal_E = Argmax[ Utility(E) ]**
> **Utility(E) = Information_Gain(E) - Cost(E) - Penalty_Redundancy(E)**

---

## 2. Ontology Learning Strategy

**[Visible Formula]:**
> **Loss_Ontology = Sum[ dist(Sample_j, Prototype_k)^2 ]**
> **Min[ Loss_Ontology ]**

---

## 3. Grounding Verification Strategy

**[Visible Formula]:**
> **Grounding_Score = Count(Verified_Provenances) / Count(Reasoning_Steps)**

**Giải thích:**
- Chỉ số này đo lường tỷ lệ các bước suy luận có bằng chứng kiểm chứng được (Verified Provenances) trên tổng số bước.

---
**Main LaTeX:**
```latex
\mathcal{L}(\theta) = \sum_{j} \| f_\theta(x_j) - c_k \|^2
\text{Score}_{G} = \frac{|P_{verified}|}{|S_{total}|}
```
