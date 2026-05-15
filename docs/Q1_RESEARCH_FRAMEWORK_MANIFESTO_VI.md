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

## 2. Các Đóng góp Khoa học Chuyên sâu (Core Academic Contributions)

### 2.1. Kiến trúc Dual-Memory Substrate (Sự hợp nhất Semantic-Observability)
*   **Chi tiết nội dung:** Đề xuất cơ chế lưu trữ song song: **Semantic Graph** (chứa các thực thể và quan hệ sự thật khách quan) và **Observability Trace Graph** (lưu trữ tiến trình suy luận, các bước nhảy logic và kết quả của các tác vụ trước đó).
*   **Căn cứ lý thuyết:** Dựa trên mô hình **Dual-Process Theory** trong tâm lý học nhận thức (Hệ thống 1 - Phản xạ nhanh và Hệ thống 2 - Lập luận chậm). Việc lưu trữ "Traces" tương ứng với bộ nhớ tình tiết (Episodic Memory) của con người.
*   **Ý nghĩa khoa học:** Giải quyết triệt để vấn đề "Contextual Amnesia" (quên ngữ cảnh thực thi) của các hệ thống RAG hiện tại. Giúp hệ thống có khả năng **Tự phản hồi hồi quy (Recursive Self-Correction)** dựa trên kinh nghiệm thay vì chỉ dựa vào xác suất ngôn ngữ.

### 2.2. Cơ chế Điều khiển Bằng chứng dựa trên Lý thuyết Thông tin (IT-Driven Evidence Control)
*   **Chi tiết nội dung:** Thay thế thuật toán truy xuất dựa trên độ tương đồng (Cosine Similarity) bằng bộ lọc **Information-Theoretic Filter**. Hệ thống chỉ chấp nhận bằng chứng có giá trị **Surprisal (S)** cao (mang lại thông tin mới) nhưng duy trì **Entropy (H)** tổng thể thấp (tính nhất quán cao).
*   **Căn cứ lý thuyết:** Dựa trên **Nguyên lý Thông tin Tối thiểu (Principle of Minimum Evidence)** và **Information Bottleneck Theory**.
*   **Ý nghĩa khoa học:** Đây là đóng góp về mặt **Kiểm soát nhiễu (Noise Suppression)**. Nó chứng minh rằng: *"Để LLM lập luận đúng, ta không cần đưa cho nó NHIỀU bằng chứng nhất, mà cần đưa cho nó lượng thông tin làm GIẢM độ bất định nhiều nhất"*. Điều này giúp tối ưu hóa cửa sổ ngữ cảnh và ngăn chặn hiện tượng "Lost in the Middle".

### 2.3. Căn chỉnh Đa tạp cho Ontology Tiềm tàng (Manifold Alignment for Latent Ontology)
*   **Chi tiết nội dung:** Sử dụng phương pháp **Contrastive Prototypical Learning** để ánh xạ các vết lập luận (traces) vào một không gian đa tạp (manifold) chứa các "nguyên mẫu suy luận" (Reasoning Prototypes).
*   **Căn cứ lý thuyết:** Dựa trên lý thuyết **Topological Data Analysis (TDA)** và **Contrastive Learning**.
*   **Ý nghĩa khoa học:** Đóng góp một phương pháp **Học không giám sát (Unsupervised Strategy Discovery)**. Hệ thống tự động nhận diện được: "Câu hỏi này cần chiến lược so sánh" hay "Câu hỏi này cần truy vấn bắc cầu", từ đó tự điều chỉnh tham số truy hồi (Adaptive Retrieval).

### 2.4. Khung Hình thức hóa tính Ổn định Grounding (Lipschitz-Stable Grounding Guarantee)
*   **Chi tiết nội dung:** Thiết lập một rào cản toán học (Safety Barrier) để giới hạn phương sai của câu trả lời dựa trên chất lượng của bằng chứng đồ thị.
*   **Căn cứ lý thuyết:** Sử dụng khái niệm **Lipschitz Continuity** trong giải tích để đo lường độ nhạy của đầu ra (Output) so với sự biến đổi của đầu vào (Evidence).
*   **Ý nghĩa khoa học (The Killer Claim):** Cung cấp một **Bằng chứng về độ tin cậy (Verifiable Reliability)**. Nghiên cứu chứng minh rằng: Nếu bằng chứng đầu vào không vượt qua ngưỡng Surprisal Threshold, hệ thống sẽ thực hiện "Epistemic Humility" (từ chối trả lời hoặc yêu cầu thêm dữ liệu) thay vì tạo ra ảo giác. Đây là bước tiến từ "AI dự đoán" sang "AI có căn cứ".

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
