# SOTA Comparison & Public Datasets Strategy

Tài liệu này xác định các đối thủ cạnh tranh (Baseline/SOTA) và các bộ dữ liệu chuẩn mực để thực hiện đánh giá thực nghiệm cho DualMemoryKG.

---

## 1. Các Đối thủ SOTA (Target Competitors)

Để bài báo có tính thuyết phục cao, bạn cần so sánh với 3 nhóm phương pháp sau:

### Nhóm 1: Graph-based RAG (Đối thủ trực tiếp)
*   **Microsoft GraphRAG:** Sử dụng Community Detection trên KG. Đây là đối thủ mạnh nhất hiện nay nhưng có nhược điểm là chi phí Indexing cực cao.
*   **G-Retriever:** Một phương pháp SOTA tích hợp GNN (Graph Neural Networks) với LLM.
*   **HippoRAG:** Sử dụng Personalized PageRank (PPR) để tìm node, rất gần với cách tiếp cận Graph Walk.

### Nhóm 2: Agentic & Reflective RAG (Đối thủ về tư duy)
*   **Self-RAG:** Sử dụng các "Reflection Tokens" để tự đánh giá câu trả lời. Đây là chuẩn mực cho các hệ thống có tính phản biện.
*   **CRAG (Corrective RAG):** Tập trung vào việc hiệu chỉnh kết quả lấy về từ web/database.
*   **Reflexion:** Framework gốc mà Agent của chúng ta đã kế thừa và phát triển lên.

### Nhóm 3: Foundational Baselines
*   **Standard Vector RAG:** (Dense Retrieval) Sử dụng OpenAI Embeddings + FAISS/ChromaDB.
*   **Naive Graph Search:** Duyệt đồ thị theo chiều rộng (BFS) cơ bản không có IG.

---

## 2. Các Bộ dữ liệu Công khai (Public Datasets)

Dựa trên kiến trúc của DualMemoryKG, tôi đề xuất sử dụng 4 bộ dữ liệu sau:

### A. HotpotQA (Multi-hop Reasoning)
*   **Tại sao:** Đây là bộ dữ liệu "phải có" cho bất kỳ hệ thống suy luận đa bước nào. 
*   **Thế mạnh của chúng ta:** Chứng minh khả năng tìm ra "cầu nối" (bridge) giữa các tài liệu thông qua `NEXT_HOP` relations.

### B. 2WikiMultiHopQA (Complex Provenance)
*   **Tại sao:** Bộ dữ liệu này yêu cầu Agent phải giải thích được "tại sao" họ chọn đường đi đó.
*   **Thế mạnh của chúng ta:** Sử dụng `EvidenceExplainer` để đối chiếu với tập nhãn giải thích (Gold Explanations).

### C. MuSiQue (The Stress Test)
*   **Tại sao:** Được mệnh danh là bộ dữ liệu Multi-hop "khó nhất" hiện nay vì tính rời rạc của bằng chứng.
*   **Thế mạnh của chúng ta:** Chứng minh cơ chế **Information-Theoretic Control** có thể tìm thấy kim đáy bể mà không bị nhiễu bởi text rác.

### D. StrategyQA (Implicit Reasoning)
*   **Tại sao:** Các câu hỏi Yes/No đòi hỏi phải suy luận ngầm (ví dụ: "Aristotle có sử dụng laptop không?").
*   **Thế mạnh của chúng ta:** Chứng minh vai trò của **Latent Ontology** trong việc ánh xạ các khái niệm lịch sử vào logic hiện đại.

---

## 3. Ma trận Đánh giá (Evaluation Matrix)

| Metric | Ý nghĩa | DualMemoryKG vs SOTA |
| :--- | :--- | :--- |
| **F1 / EM** | Độ chính xác của đáp án. | Kỳ vọng: Tương đương hoặc cao hơn GraphRAG. |
| **Groundedness** | Tỷ lệ câu trả lời bám sát bằng chứng. | **Kỳ vọng: Thắng tuyệt đối nhờ Reasoning Equilibrium.** |
| **Token-to-Solution Ratio** | Số token tiêu tốn cho mỗi câu đúng. | **Kỳ vọng: Thắng nhờ Entropy Pruning.** |
| **Path Fidelity** | Độ khớp giữa đường đi của Agent và Gold Path. | Kỳ vọng: Cao hơn HippoRAG nhờ Traversal Policy. |

---

## 4. Phần Mở rộng nâng cao (Elite Tier Extension)

Nếu mục tiêu là các hội nghị như **NeurIPS/ICLR**, bạn nên xem xét thêm các hạng mục sau:

### Các SOTA bổ sung:
*   **Graph-of-Thoughts (GoT):** Framework cho phép mô hình hóa suy luận dưới dạng đồ thị tùy ý (không chỉ là chuỗi). Chúng ta sẽ so sánh về tính hiệu quả của việc kiểm soát bằng chứng.
*   **BGE-Reranker + VectorRAG:** Baseline mạnh nhất của ngành công nghiệp hiện nay. Chứng minh IG-Selection sắc bén hơn Re-ranking thuần túy.
*   **ToT (Tree-of-Thoughts):** So sánh về khả năng backtrack (quay lui) khi gặp ngõ cụt.

### Các Bộ dữ liệu "Sát thủ":
*   **HaluEval (The Hallucination Benchmark):** Chứng minh DualMemoryKG có thể phát hiện và loại bỏ các đoạn văn bản gây ảo giác.
*   **ComplexWebQuestions:** Kiểm tra khả năng xử lý các Ontology phức tạp của Web.
*   **WikiHop:** Bài test về độ bao phủ tri thức rộng.

## 5. Lời khuyên cuối cùng về Chiến lược thực nghiệm

"Đừng chạy tất cả mọi thứ". Hãy chọn **MuSiQue** cho độ khó, **HotpotQA** cho tính phổ biến và **HaluEval** để làm điểm nhấn Scientific đóng góp về tính tin cậy. Ba bộ dữ liệu này là đủ để tạo nên một bộ hồ sơ thực nghiệm "không thể đánh bại" cho bất kỳ tạp chí Q1 nào.
