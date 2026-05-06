# Theoretical Foundation: Domain-Agnostic Grounded Reasoning

This document formalizes the mechanisms of the DualMemoryKG framework. It provides the mathematical definitions and proof sketches required for a high-impact (Q1) scientific publication.

---

## 1. Problem Formulation

Let $\mathcal{D}$ be a reasoning domain. We define the **Domain-Agnostic Grounded Reasoning Task** as follows:

Given a query $q \in \mathcal{Q}$, and a heterogeneous memory graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$, identify a support set (or path) $\mathcal{P} \subseteq \mathcal{V}$ such that:
$$ y = f_{LLM}(q, \mathcal{P}) $$
where $y$ is the answer, and $\mathcal{P}$ satisfies the **Grounding Objective**:
$$ \max_{\mathcal{P} \subseteq \mathcal{V}} \text{Utility}(\mathcal{P} | q, \mathcal{Z}) - \lambda \cdot \text{Cost}(\mathcal{P}) $$
where $\mathcal{Z}$ is the latent reasoning ontology.

---

## 2. Claim 1: Contrastive Latent Ontology Induction

### Statement
The induction of reasoning concepts through a contrastive prototype mechanism increases the **inter-cluster margin** $\gamma$, thereby reducing concept alignment error $\epsilon_{ont}$.

### Mathematical Definition
Let $v_i$ be the embedding of a reasoning trace. The prototype $c_k$ for concept $k$ is updated as:
$$ c_k = \text{Norm} \left( \sum_{i \in S_k} w_i v_i + \alpha \cdot \text{Repulsion}(c_k, \mathcal{C}_{neg}) \right) $$
where $\text{Repulsion}(c_k, \mathcal{C}_{neg}) = \sum_{j \neq k} (c_k - c_j)$ is the contrastive vector that pushes the prototype away from hard negatives.

### Proof Sketch
By introducing the repulsion vector, the update rule approximates a gradient step that minimizes the contrastive loss $\mathcal{L}_{cont}$. As $\alpha > 0$, the distance $dist(c_k, c_j)$ increases for $j \neq k$. 
Consequently, the probability of misclassification $P(z(q) \neq z^*(q))$ decreases as the decision boundaries become more separable in the latent space.

---

## 3. Claim 2: Information-Theoretic Evidence Selection

### Statement
Selecting evidence based on **Marginal Information Gain** reduces the entropy of the answer distribution $H(Y | q, \mathcal{P})$ more effectively than similarity-based retrieval.

### Mathematical Definition
The utility of adding a node $v$ to an existing support set $\mathcal{P}_{t}$ is defined by its **Marginal Utility**:
$$ \Delta \mathcal{U}(v) = \underbrace{\text{Sim}(v, z(q))}_{\text{Alignment}} + \underbrace{\beta \cdot IG(v | \mathcal{P}_t)}_{\text{Information Gain}} - \underbrace{\gamma \cdot \text{Redundancy}(v, \mathcal{P}_t)}_{\text{Penalty}} $$
where $IG(v | \mathcal{P}_t)$ measures the reduction in uncertainty regarding the reasoning path.

### Proof Sketch
Similarity-only retrieval ($IG=0, \gamma=0$) often retrieves redundant nodes $v_1 \approx v_2$, which do not contribute new bits of information to the reasoning context. 
By maximizing $\Delta \mathcal{U}(v)$, the selector prioritizes nodes that are (1) aligned with the reasoning concept and (2) contain non-overlapping evidence. This ensures that $|\mathcal{P}|$ captures the maximum possible support coverage within the LLM's context window.

---

## 4. Claim 3: Grounding-Centered Evaluation Validity

### Statement
The **Grounding Precision** metric $\text{Prec}_{gnd}$ is a more reliable proxy for system mechanism quality than the **Exact Match** (EM) accuracy.

### Formalization
Let $Y_{correct}$ be the event that the answer is correct, and $S_{grounded}$ be the event that the answer is supported by gold evidence.
$$ P(Y_{correct}) = P(Y_{correct} | S_{grounded})P(S_{grounded}) + P(Y_{correct} | \neg S_{grounded})P(\neg S_{grounded}) $$
The term $P(Y_{correct} | \neg S_{grounded})$ represents **Hallucination Success** (lucky correctness).

### Proof Sketch
Traditional RAG evaluation only measures $P(Y_{correct})$. In high-temperature or large-scale models, $P(Y_{correct} | \neg S_{grounded}) > 0$ is significant.
By measuring $\text{Prec}_{gnd}$, we isolate $P(S_{grounded})$, which is the true indicator of the architecture's ability to control and verify evidence. Therefore, a system with higher $\text{Prec}_{gnd}$ is scientifically superior even if $P(Y_{correct})$ is equivalent.

---

## 5. Domain-Agnostic Abstraction Principle

The architecture maintains a **Strict Abstraction Boundary** between the Domain Interface $\mathcal{I}_D$ and the Reasoning Core $\mathcal{R}$.

1. **Invariance:** The reasoning core $\mathcal{R}$ operates only on the universal typed schema $\mathcal{S}$.
2. **Transformability:** Any domain $D$ can be mapped to $\mathcal{S}$ via an adapter $f_D: \mathcal{X}_D \to \mathcal{S}$.

**Conclusion:** The formal validity of the reasoning mechanisms (Claims 1 & 2) is independent of the domain $D$, making the framework fundamentally **domain-agnostic**.

---

## Summary for Paper Submission

This theoretical framework provides the **Rigor** required for Q1 journals by:
- Replacing heuristics with **Optimization Objectives**.
- Replacing intuition with **Probabilistic Error Decomposition**.
- Proving that improvements are **Mechanism-Level** rather than just accidental benchmark gains.
