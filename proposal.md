# ĐỀ XUẤT NGHIÊN CỨU (PHIÊN BẢN NÂNG CAO – Q1)

## Học cấu trúc suy luận và từ vựng tri thức để giảm Hallucination trong LLM Agents

---

# 1. Giới thiệu

Các hệ thống LLM agent hiện đại gặp hạn chế nghiêm trọng về **hallucination**, đặc biệt trong các bài toán cần:

* suy luận nhiều bước
* truy xuất tri thức
* tương tác với môi trường

Framework Dual-Memory Knowledge Graph (DualMemoryKG) đề xuất:

* Semantic Memory (tri thức)
* Observability Memory (trace suy luận)

Tuy nhiên, hệ thống này tồn tại hai hạn chế cốt lõi:

1. **Tái sử dụng memory theo heuristic (không học)**
2. **Phụ thuộc vào shared vocabulary thiết kế thủ công**

---

# 2. Khoảng trống nghiên cứu (Research Gap)

Các phương pháp hiện tại như:

* GraphRAG
* Self-RAG
* Reflexion

đã cải thiện hallucination nhưng:

### ❌ Chưa giải quyết 2 vấn đề quan trọng:

### (1) Không học cấu trúc suy luận

→ reasoning vẫn phụ thuộc prompt hoặc heuristic

### (2) Vocabulary không adaptive

→ shared schema:

* intent
* attribute
* entity

👉 được define thủ công → không mở rộng sang domain mới

---

# 3. Mục tiêu nghiên cứu

Xây dựng một framework:

> **Learning Structured Reasoning and Adaptive Knowledge Vocabulary for LLM Agents**

Cụ thể:

* Học policy suy luận trên graph
* Tự động học vocabulary (ontology) từ dữ liệu
* Giảm hallucination và tăng khả năng tổng quát

---

# 4. Phương pháp đề xuất

---

# 4.1 Tổng quan hệ thống

Pipeline:

```id="system_v2"
Query q
  ↓
Neural Vocabulary Encoder
  ↓
Dual-Memory Graph Construction
  ↓
Graph Reasoning Policy (Learning-based)
  ↓
LLM Execution
  ↓
Output + Feedback
  ↓
Memory & Vocabulary Update
```

---

# 4.2 Automatic Vocabulary Learning (Đóng góp mới quan trọng)

## ❗ Vấn đề:

Vocabulary hiện tại:

* handcrafted
* domain-specific
* không mở rộng

---

## 💡 Đề xuất:

Học vocabulary từ dữ liệu:

### Input:

* query
* reasoning traces
* knowledge graph

---

### Output:

* latent vocabulary:

  * intent embedding
  * attribute embedding
  * entity embedding

---

## ⚙️ Cách thực hiện:

### 1. Embedding-based clustering

$$
z_i = Encoder(x_i)
$$

→ cluster thành:

* intents
* attributes

---

### 2. Contrastive learning

* positive: cùng loại reasoning
* negative: khác loại

---

### 3. Dynamic vocabulary update

* thêm / xoá concept theo data distribution

---

👉 Kết quả:

> Vocabulary không còn là rule-based → trở thành learnable representation

---

# 4.3 Dual-Memory Graph (Nâng cấp)

Graph gồm:

## Node:

* knowledge (semantic)
* reasoning step (observability)
* learned concepts (vocabulary)

---

## Edge:

* relation
* causal
* semantic similarity

---

👉 Đây là:

> unified graph: knowledge + reasoning + vocabulary

---

# 4.4 Graph-based Reasoning Policy Learning

## State:

$$
s = (current\ node, query)
$$

## Action:

$$
a = next\ node
$$

## Policy:

$$
\pi(a|s)
$$

---

## Reward:

$$
r = Accuracy - Hallucination
$$

---

👉 Agent học cách:

* traverse graph
* chọn reasoning path tối ưu

---

# 4.5 Memory Update

Sau mỗi episode:

* thêm trace mới
* update vocabulary
* refine graph

---

# 5. Insight lý thuyết

---

## Insight 1:

Hallucination = sai đường suy luận

---

## Insight 2:

Observability memory = tập các đường suy luận đúng

---

## Insight 3:

Vocabulary learning giúp:

* hiểu cấu trúc task tốt hơn
* tăng generalization

---

## Insight 4:

Policy learning giúp:

* chọn đường đi tối ưu
* giảm error propagation

---

# 6. Thiết kế thực nghiệm

---

## 6.1 Dataset

### Reasoning:

* HotpotQA
* GSM8K
* MMLU

---

## 6.2 Baseline

* GPT-4
* RAG
* Self-RAG
* GraphRAG
* Reflexion

---

## 6.3 Metric

* Accuracy
* Hallucination rate
* Faithfulness

---

## 6.4 Ablation

| Variant                | Ý nghĩa           |
| ---------------------- | ----------------- |
| No vocabulary learning | test contribution |
| No policy learning     | test reasoning    |
| No observability       | test memory       |

---

## 6.5 Generalization test

* train domain A → test domain B
  → chứng minh vocabulary learning hiệu quả

---

# 7. Đóng góp chính

1. **Automatic Vocabulary Learning cho LLM agents**
2. **Graph-based reasoning policy learning**
3. Unified framework:

   * knowledge + reasoning + vocabulary
4. Giảm hallucination mạnh và tăng generalization

---

# 8. Tính mới (Novelty)

| Thành phần     | Bài cũ      | Đề xuất         |
| -------------- | ----------- | --------------- |
| Vocabulary     | handcrafted | learned         |
| Memory usage   | heuristic   | policy-based    |
| Reasoning      | prompt      | graph traversal |
| Generalization | thấp        | cao             |

---

# 9. Kế hoạch thực hiện

| Giai đoạn          | Thời gian |
| ------------------ | --------- |
| Reproduce baseline | 1–2 tuần  |
| Vocabulary module  | 1–2 tuần  |
| Graph policy       | 2–3 tuần  |
| Experiment         | 2 tuần    |
| Writing            | 2 tuần    |

---

# 10. Kết luận

Đề tài này mở rộng DualMemoryKG theo hướng học:

* cách suy luận
* cách biểu diễn tri thức

→ tạo ra một hệ thống LLM agent có khả năng:

* giảm hallucination
* tổng quát hóa tốt
* phù hợp công bố Q1

---

# 11. Tiêu đề đề xuất

**Learning Reasoning Policies and Adaptive Knowledge Vocabulary for Hallucination-Resilient LLM Agents**

---
