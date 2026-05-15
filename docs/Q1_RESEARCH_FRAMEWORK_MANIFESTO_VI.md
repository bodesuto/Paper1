# DualMemoryKG: Bản Tuyên ngôn Khung Nghiên cứu & Chiến lược Công bố Q1

Tài liệu này hệ thống hóa toàn bộ giá trị học thuật của dự án **DualMemoryKG**, phục vụ cho việc viết bản thảo bài báo (Manuscript) và bảo vệ luận văn.

---

## 1. Động lực & Mục tiêu Nghiên cứu (Motivation & Goals)

### 1.1. Động lực (Research Motivation)
*   **Vấn đề:** Các hệ thống Retrieval-Augmented Generation (RAG) hiện nay vẫn gặp phải tình trạng **"Hư cấu có căn cứ"** (Grounded Hallucination). Nguyên nhân là do LLM bị "ngộp" bởi các bằng chứng dư thừa, thiếu tính liên kết logic và không có khả năng tự quan sát quá trình suy luận của chính mình.
*   **Khoảng trống tri thức:** Sự tách biệt giữa không gian vector mập mờ (Semantic) và đồ thị logic cứng nhắc (Symbolic). LLM thiếu một "Bộ nhớ Quan sát" (Observability Memory) để học từ những vết sai lầm trong quá khứ.

### 1.2. Mục tiêu (Research Goals)
*   Xây dựng hệ thống **Dual-Memory Substrate** đồng bộ hóa giữa sự thật khách quan và vết trải nghiệm chủ quan.
*   Thiết lập cơ chế **Information-Theoretic Control** để lọc bằng chứng dựa trên nguyên lý giảm thiểu độ bất định (Uncertainty Reduction).
*   Đề xuất phương pháp **Contrastive Latent Ontology Induction** để tự động hóa việc hiểu ý định suy luận mà không cần gán nhãn thủ công.

---

## 2. Đóng góp Khoa học (Academic Contributions)

1.  **Kiến trúc Dual-Memory (Semantic-Observability Integration):** Đóng góp một cơ chế lưu trữ kép cho phép hệ thống "nhớ" được kết quả suy luận thành công và thất bại, chuyển đổi từ RAG tĩnh sang **Interactive Knowledge Evolution**.
2.  **Cơ chế Traversal Policy dựa trên Lý thuyết Thông tin:** Thay vì truy xuất dựa trên độ tương đồng (Similarity), DualMemoryKG truy xuất dựa trên **Surprisal (S)** và **Information Gain (IG)**. Đây là đóng góp về mặt thuật toán giúp tối ưu hóa cửa sổ ngữ cảnh (Context Window).
3.  **Mô hình Hình thức hóa Ảo giác (Formal Taxonomy of Hallucination):** Đề xuất khung chẩn đoán **Deep Error Decomposition** (E-Ont, E-Trav, E-Gnd), cung cấp một công cụ định lượng cho phép cộng đồng nghiên cứu giải phẫu sâu các lỗi của RAG.
4.  **Chứng minh tính Lipschitz-Stability trong Grounding:** Đưa ra lập luận toán học về việc giới hạn sai số của câu trả lời thông qua các "Rãnh an toàn" (Safety barriers) của bằng chứng đồ thị.

---

## 3. Phương pháp So sánh & Đánh giá (Evaluation Methodology)

### 3.1. Các hệ thống Baseline & SOTA đối trọng
Để chứng minh sự vượt trội, DualMemoryKG sẽ được so sánh với 4 đối thủ mạnh nhất hiện nay:
-   **Naive RAG (Vector-only):** Chuẩn truy xuất ngữ nghĩa cơ bản.
-   **GraphRAG (Microsoft):** Đại diện cho hướng tiếp cận đồ thị tri thức thuần túy.
-   **Self-RAG:** Đại diện cho hướng tiếp cận LLM tự đánh giá.
-   **HyDE (Hypothetical Document Embeddings):** Đại diện cho hướng tiếp cận mở rộng truy vấn.

### 3.2. Hệ thống Metric đa chiều (Benchmark Metrics)
Nghiên cứu sử dụng 3 nhóm chỉ số để đánh giá toàn diện:
1.  **Nhóm Chất lượng (Effectiveness):**
    -   *Exact Match (EM) & F1 Score*: Đo lường độ chính xác câu trả lời.
    -   *Faithfulness (DeepEval)*: Tỷ lệ câu trả lời hoàn toàn dựa trên bằng chứng, không ảo giác.
2.  **Nhóm Hiệu năng Thông tin (Information Efficiency):**
    -   *Marginal Information Gain (MIG)*: Lượng thông tin hữu ích thu được trên mỗi node truy xuất.
    -   *Context Redundancy*: Đo lường sự dư thừa của văn bản đưa vào Prompt.
3.  **Nhóm Chẩn đoán lỗi (Diagnostic):**
    -   *Ontology Alignment Score*: Độ khớp giữa loại câu hỏi và chiến lược truy xuất.
    -   *Grounding Precision/Recall*: Độ chính xác của việc chọn đúng Node tri thức cần thiết.

---

## 4. Kì vọng Kết quả & Kết luận (Expected Results & Conclusion)

*   **Kì vọng:** DualMemoryKG sẽ đạt được điểm **Faithfulness** cao hơn đáng kể (>15%) so với GraphRAG trong các câu hỏi phức tạp đa chặng (multi-hop).
*   **Đường cong hiệu suất:** Chứng minh được sự cân bằng tối ưu giữa **Độ trễ (Latency)** và **Độ chính xác**, nơi Information-Theoretic Control giúp giảm 30% lượng dữ liệu đầu vào mà vẫn giữ nguyên accuracy.
*   **Kết luận:** Nghiên cứu khẳng định rằng tương lai của AI tin cậy nằm ở sự phối hợp giữa "Tri thức thế giới" và "Kinh nghiệm thực thi".

---

## 5. Hướng Ứng dụng & Mở rộng (Future Work)

### 5.1. Ứng dụng Thực tiễn
-   **Y tế/Pháp lý:** Những nơi mà ảo giác 1% cũng dẫn đến hậu quả nghiêm trọng.
-   **Bảo trì hệ thống phức tạp:** Sử dụng Observability Graph để chẩn đoán lỗi trong các hạ tầng phần mềm quy mô lớn.

### 5.2. Mở rộng Nghiên cứu Q1 Tương lai
-   **Multi-Agent Collaborative Dual-Memory:** Mở rộng thành hệ thống đa tác nhân, mỗi tác nhân quản lý một phân vùng tri thức khác nhau.
-   **Cross-Modal Grounding:** Tích hợp bộ nhớ hình ảnh/video vào đồ thị Dual-Memory.
-   **Online Plasticity:** Cơ chế cập nhật trọng số đồ thị theo thời gian thực (Real-time weight updating) mà không cần bước offline processing.
