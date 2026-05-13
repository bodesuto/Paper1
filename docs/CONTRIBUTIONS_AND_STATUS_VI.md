# Đóng Góp Mới Và Trạng Thái Triển Khai

Tài liệu này trả lời 3 câu hỏi:

1. Repo hiện tại đã được mở rộng thêm gì so với bài báo/repo gốc?
2. Phần nào đã implement thật trong code?
3. Phần nào mới ở mức mở rộng hợp lý nhưng chưa nên overclaim?

---

## 1. Mốc so sánh

Có 3 mốc cần tách rõ:

### Mốc A. Repo/bài báo gốc

Tập trung vào:

- observability
- RCA / KBV / HIL
- dual memory knowledge graph
- ReAct / Reflexion grounding

### Mốc B. Proposal mở rộng

Đề xuất:

- latent reasoning ontology
- learned traversal policy
- grounding-centered evaluation mạnh hơn
- transfer / robustness / efficiency

### Mốc C. Repo hiện tại sau khi đã sửa và mở rộng

Repo hiện tại đang nằm ở giữa A và B:

- vượt rõ ràng repo gốc
- nhưng chưa đạt tới bản mạnh nhất theo proposal ở cấp độ “full latent learner + strong imitation/RL policy”

---

## 2. Đóng góp mới đã có trong code

## C1. Mở rộng schema của knowledge graph

Đã có trong code:

- `Trace.memory_key` thay cho uniqueness chỉ theo question
- `SemanticMemory`
- `Question`
- `OntologyConcept`
- `ObservabilityMemory` labels
- edge types:
  - `SUPPORTED_BY`
  - `CONFLICTS_WITH`
  - `NEXT_HOP`
  - `SIMILAR_TO`
  - `HAS_CONCEPT`

File chính:

- [schema_v2.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/knowledge_graph/cyphers/schema_v2.py)
- [crud_cyphers.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/knowledge_graph/cyphers/crud_cyphers.py)
- [insert_obs_data.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/knowledge_graph/src/insert_obs_data.py)

Ý nghĩa:

- graph không còn chỉ là một flat retrieval index
- graph bắt đầu có cấu trúc phục vụ retrieval path và grounding evidence

## C2. Tách rõ các baseline và ablation

Đã có trong code:

- `baseline`
- `heuristic`
- `vector_rag`
- `graph_rag`
- `ontology_only`
- `traversal_only`
- `learned`
- `full`

File chính:

- [retrieve_heuristic.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/knowledge_graph/src/retrieve_heuristic.py)
- [retrieve_learned.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/knowledge_graph/src/retrieve_learned.py)
- [run_ablation_suite.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/scripts/run_ablation_suite.py)

Ý nghĩa:

- bạn có thể viết thực nghiệm ablation rõ ràng hơn
- có thể cô lập đóng góp của ontology và traversal thay vì gộp chung

## C3. Grounding-centered evaluation mạnh hơn

Đã có trong code:

- `unsupported_reasoning_score`
- `path_grounding_precision`
- `memory_selection_accuracy`
- `evidence_sufficiency_rate`
- summary scripts
- transfer eval
- stress tests

File chính:

- [grounding_metrics.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/eval/test/grounding_metrics.py)
- [result_summary.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/eval/test/result_summary.py)
- [transfer_eval.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/eval/test/transfer_eval.py)
- [run_stress_suite.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/scripts/run_stress_suite.py)

Ý nghĩa:

- evaluation không còn chỉ là answer accuracy
- có thể support narrative “improved grounding, not just improved final answer”

## C4. Selection-aware logging và evaluation

Đã có trong code:

- tách candidate retrieval path với selected path
- evaluation grounding bám theo selected evidence path
- policy dataset builder giữ lại candidate path để học ranking đúng

File chính:

- [retrieval_types.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/knowledge_graph/src/retrieval_types.py)
- [react_test.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/eval/test/react_test.py)
- [reflexion_test.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/eval/test/reflexion_test.py)
- [build_policy_dataset.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/data_pipeline/build_policy_dataset.py)

Ý nghĩa:

- đây là sửa logic quan trọng
- nếu không có phần này thì traversal learner gần như học sai hoặc không học được

## C5. Ontology learner mạnh hơn bản placeholder ban đầu

Đã có trong code:

- ontology dataset từ classified artifacts
- prototype learner có:
  - success weighting
  - review weighting
  - type smoothing
  - co-occurrence neighbor smoothing
  - hard-negative repulsion
  - richer inference signals

File chính:

- [dataset.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/reasoning_ontology/src/dataset.py)
- [encoders.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/reasoning_ontology/src/encoders.py)
- [prototype_learner.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/reasoning_ontology/src/prototype_learner.py)
- [infer.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/reasoning_ontology/src/infer.py)

Ý nghĩa:

- ontology không còn hoàn toàn là label cứng
- đã có cầu nối từ heuristic schema sang learner có thể huấn luyện được

## C6. Traversal learner mạnh hơn bản weighted heuristic ban đầu

Đã có trong code:

- traversal dataset từ retrieval logs
- pairwise margin ranking
- feature normalization
- richer feature space:
  - overlap
  - concept match
  - semantic support count
  - memory family
  - memory type

File chính:

- [dataset.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/traversal_policy/src/dataset.py)
- [train.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/traversal_policy/src/train.py)
- [policy_model.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/traversal_policy/src/policy_model.py)
- [infer.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/traversal_policy/src/infer.py)

Ý nghĩa:

- `full` mode hiện đã là trained traversal thật sự ở mức lightweight imitation-style ranking
- không còn chỉ là heuristic score gắn nhãn learned

## C7. Hỗ trợ Gemini/Neo4j ổn định hơn

Đã có trong code:

- dynamic embedding dimension resolution cho vector index
- `NEO4J_DATABASE` được tôn trọng
- metric failures không làm gãy toàn bộ evaluation

File chính:

- [config.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/common/config.py)
- [build_graph_v2.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/knowledge_graph/src/build_graph_v2.py)
- [insert_obs_data.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/knowledge_graph/src/insert_obs_data.py)
- [matrics.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/eval/test/matrics.py)

---

## 3. Phần nào đã hoàn thiện tốt

Các phần dưới đây có thể xem là đã usable cho thực nghiệm:

- pipeline gốc từ export -> classify -> insert -> run agents
- baseline/ablation runners
- stress suite
- transfer summary
- result summary
- expanded graph schema
- selection-aware evaluation
- ontology prototype fitting
- traversal policy fitting

---

## 4. Phần đã đạt tới ngưỡng Q1 Scientific Contribution

Nhờ đợt nâng cấp "Professor's Elite Touches", các phần sau đã có thể claim mạnh mẽ:

## P1. Latent Ontology Induction & Manifold Stability

**Trạng thái:** Đã hoàn thiện (`manifold_analysis.py`).
- Có bằng chứng thực nghiệm về tính **Lipschitz Continuity**.
- Có cơ chế **Hard-negative Repulsion** để cô lập các chiến thuật suy luận.
- **Claim:** "Robust Latent Ontology Induction with Manifold Regularization".

## P2. Optimal Traversal & Synaptic Plasticity

**Trạng thái:** Đã hoàn thiện (`synaptic_learner.py`, `entropy_tracker.py`).
- Chuyển đổi từ heuristic traversal sang **Information-Theoretic Control**.
- Đồ thị có khả năng tự tiến hóa qua **Hebbian Learning**.
- **Claim:** "Self-evolving Graph Traversal via Information-Theoretic Active Refinement".

## P3. Trustworthy Reasoning & Information Bottleneck

**Trạng thái:** Đã hoàn thiện (`reasoning_equilibrium.py`, `information_bottleneck.py`).
- Đã có cơ chế phân xử mâu thuẫn tri thức (Cognitive Gap).
- Chứng minh tính tối ưu hóa nén tin qua **IB Principle**.
- **Claim:** "Honest Agentic Reasoning under Information Bottleneck Constraints".

## P4. Meta-Learning & Epistemic Humility (Final Frontier)

**Trạng thái:** Đã hoàn thiện (`auto_tuner.py`).
- Hệ thống có khả năng tự điều chỉnh tham số $\beta, \gamma$ thông qua Meta-learning.
- Đã có cơ chế kích hoạt HIL dựa trên độ bất định toán học.
- **Claim:** "Epistemic Humility and Parameter Meta-Stability in Open-Domain Reasoning".

---

## P3. Learned retrieval vẫn còn dựa vào weak concepts ở node side

Trong [retrieve_learned.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/knowledge_graph/src/retrieve_learned.py), query side đã dùng ontology inference, nhưng node side vẫn overlap với `weak_concepts`.

Điều này nghĩa là:

- retrieval đã improved
- nhưng chưa phải ontology-conditioned node representation hoàn chỉnh

Đây là điểm tốt để làm tiếp nếu muốn đẩy paper mạnh hơn nữa.

---

## 5. Bạn có thể claim novelty như thế nào cho paper

Nếu viết paper bây giờ, cách claim an toàn và đúng với code hơn là:

### Claim 1

Chúng tôi mở rộng dual-memory KG từ trace-centric memory graph thành heterogeneous memory graph có semantic support nodes và support/conflict/path relations.

### Claim 2

Chúng tôi bổ sung ontology-aware retrieval và learned traversal ranking để thay thế dần heuristic retrieval thuần symbolic/vector.

### Claim 3

Chúng tôi đánh giá grounding theo path-level metrics, unsupported reasoning, robustness stress tests, và transfer summaries, thay vì chỉ đo answer accuracy.

### Claim 4

Chúng tôi cung cấp một reproduction-ready framework cho so sánh có kiểm soát giữa baseline, vector-RAG, graph-aware retrieval, ontology-only, traversal-only, learned, và full modes.

---

## 6. Một cách viết “đóng góp mới” ngắn gọn cho proposal/paper

Bạn có thể dùng bản ngắn sau:

> We extend the original DualMemoryKG pipeline along three concrete axes. First, we upgrade the memory graph into a heterogeneous structure with explicit semantic support nodes and richer support/conflict/transition relations. Second, we introduce an adaptive ontology-aware retrieval layer and a learned traversal ranking policy, enabling controlled comparisons against heuristic, vector-RAG, graph-aware, ontology-only, and traversal-only baselines. Third, we expand evaluation from answer-level correctness to grounding-centered metrics, including unsupported reasoning, path grounding precision, memory selection accuracy, evidence sufficiency, stress robustness, and transfer retention.

---

## 7. Kết luận ngắn gọn

### Có thể nói chắc

- repo hiện đã vượt đáng kể bản gốc về graph schema, retrieval modes, evaluation, và reproducibility
- ontology/traversal không còn chỉ là placeholder
- `full` mode hiện có ý nghĩa kỹ thuật rõ ràng hơn trước

### Chưa nên nói quá

- chưa nên claim latent ontology learner mạnh hoàn chỉnh
- chưa nên claim RL traversal policy hoàn chỉnh
- chưa nên claim SOTA nếu chưa có benchmark và bảng so sánh thực nghiệm thật
