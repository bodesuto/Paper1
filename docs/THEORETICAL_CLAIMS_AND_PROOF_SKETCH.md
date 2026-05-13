# Theoretical Foundation: Domain-Agnostic Grounded Reasoning

This document formalizes the mechanisms of the DualMemoryKG framework. It provides the mathematical definitions and proof sketches required for a high-impact (Q1) scientific publication.

---

## 0. Mathematical Notations

| Symbol | Description | Domain |
| :--- | :--- | :--- |
| $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ | Heterogeneous Memory Knowledge Graph | Graph Space |
| $\mathcal{P} \subseteq \mathcal{V}$ | Support Evidence Set (Retrieval Path) | Discrete Space |
| $q, y$ | Query and Answer (Natural Language) | Semantic Space |
| $\mathcal{Z}$ | Latent Reasoning Ontology (Prototypes) | Embedding Space |
| $H(Y|q, \mathcal{P})$ | Conditional Entropy of the Answer distribution | Information Theory |
| $IG(v | \mathcal{P}_t)$ | Marginal Information Gain of node $v$ | Information Theory |
| $\alpha, \beta, \gamma$ | Hyperparameters for Repulsion, IG, and Penalty | Parameter Space |

---

## 1. Problem Formulation

Let $\mathcal{D}$ be a reasoning domain. We define the **Domain-Agnostic Grounded Reasoning Task** as follows:

Given a query $q \in \mathcal{Q}$, and a heterogeneous memory graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$, identify an optimal support set $\mathcal{P}^* \subseteq \mathcal{V}$ such that:
$$ y = f_{\text{LLM}}(q, \mathcal{P}^*) $$
where $y$ is the generated response, and $\mathcal{P}^*$ satisfies the **Grounded Maximum Utility Objective**:
$$ \mathcal{P}^* = \arg\max_{\mathcal{P} \subseteq \mathcal{V}} \left[ \text{Utility}(\mathcal{P} \mid q, \mathcal{Z}) - \lambda \cdot \text{Cost}(\mathcal{P}) \right] $$
where $\mathcal{Z}$ represents the learned latent reasoning ontology governing the traversal policy.

---

## 2. Claim 1: Contrastive Latent Ontology Induction

### Statement
The induction of reasoning concepts through a contrastive prototype mechanism maximizes the **inter-cluster margin** $\Gamma$, thereby minimizing the concept alignment error $\epsilon_{\text{ont}}$.

### Mathematical Definition
Let $v_i \in \mathbb{R}^d$ be the embedding of a behavioral reasoning trace. Each prototype $c_k$ for reasoning concept $k$ is updated via a **Contrastive-Hebbian** rule:
$$ c_k^{(t+1)} = \text{Norm} \left( \sum_{i \in S_k} w_i v_i + \alpha \cdot \text{Repulsion}(c_k, \mathcal{C}_{\text{neg}}) \right) $$
where the Repulsion force is defined by:
$$ \text{Repulsion}(c_k, \mathcal{C}_{\text{neg}}) = \sum_{j \neq k} \frac{c_k - c_j}{\|c_k - c_j\|^2} $$
This force pushes the prototype away from hard-negative reasoning styles in the latent space.

### Proof Sketch
The update rule effectively minimizes a contrastive loss function $\mathcal{L}_{\text{cont}}$ by performing gradient descent in the embedding space. As the repulsion factor $\alpha$ increases, the Lipschitz constant of the decision boundary improves, leading to a strictly larger margin $\Gamma$ between reasoning styles. This ensures that the agent selects the correct retrieval policy for a given query type with higher probability.

---

## 3. Claim 2: Information-Theoretic Evidence Selection

### Statement
Selecting evidence nodes based on **Marginal Information Gain** (IG) ensures that the conditional entropy $H(Y | q, \mathcal{P})$ is minimized at a faster rate than traditional similarity-based methods.

### Mathematical Definition
The utility gain $\Delta \mathcal{U}(v)$ for adding a new node $v$ to the current evidence set $\mathcal{P}_t$ is:
$$ \Delta \mathcal{U}(v) = \underbrace{\text{CosineSim}(v, \mathcal{Z}(q))}_{\text{Domain Alignment}} + \beta \cdot \underbrace{\text{IG}(v \mid \mathcal{P}_t)}_{\text{Surprisal Control}} - \gamma \cdot \underbrace{\text{Redundancy}(v, \mathcal{P}_t)}_{\text{Information Overlap}} $$
where $\text{IG}(v \mid \mathcal{P}_t)$ is defined as the reduction in uncertainty concerning the gold reasoning path:
$$ \text{IG}(v \mid \mathcal{P}_t) = H(\text{Path} \mid \mathcal{P}_t) - H(\text{Path} \mid \mathcal{P}_t \cup \{v\}) $$

### Proof Sketch
Traditional RAG relies on $\beta=0, \gamma=0$, frequently resulting in a collapsed support set where $v_1 \approx v_2 \approx ... \approx v_n$. Our objective function penalizes high mutual information $I(v; \mathcal{P}_t)$ between the new node and existing nodes. This forces the agent to explore "diverse but relevant" edges in the Knowledge Graph, maximizing the coverage of the context window with unique bits of evidence.

---

## 4. Claim 3: Grounding-Centered Evaluation Validity

### Statement
**Grounding-based accuracy** $\text{Acc}_{\text{gnd}}$ provides a more rigorous indicator of system stability than surface-level **Exact Match** (EM) metrics.

### Probabilistic Formalization
Let $Y$ be the correctness event. We decompose the probability of success into:
$$ P(Y=1) = \underbrace{P(Y=1 \mid \text{Grounded})P(\text{Grounded})}_{\text{Intrinsic Capability}} + \underbrace{P(Y=1 \mid \neg \text{Grounded})P(\neg \text{Grounded})}_{\text{Hallucination Bias}} $$
Our framework aims to maximize $P(\text{Grounded})$ and minimize $P(Y=1 \mid \neg \text{Grounded})$, effectively eliminating "lucky" correct answers generated through internal LLM bias rather than external evidence.

---

## 5. Domain-Agnostic Abstraction Principle

The framework maintains a **Strict Abstraction Barrier** between the Domain-Specific Logic and the Reasoning Engine:
1. **Invariance:** The reasoning core operates exclusively on the abstract schema $\mathcal{S}$.
2. **Transferability:** A mapping function $f_D: \text{Domain}_D \to \mathcal{S}$ allows any vertical domain (Legal, Medical, Technical) to utilize the same grounded reasoning policy.

**Scientific Impact:** This decoupling proves that the improvements in reasoning capability are **Structural** and **Universal**, making the DualMemoryKG a general-purpose foundation for trustworthy agents.
