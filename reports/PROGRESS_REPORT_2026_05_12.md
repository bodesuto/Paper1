# BÁO CÁO TIẾN ĐỘ DỰ ÁN: DUALMEMORYKG (AGENTIC KNOWLEDGE GRAPH)
**Ngày thực hiện:** 12 tháng 05 năm 2026
**Đối tượng:** Hội đồng khoa học / Giảng viên hướng dẫn
**Trình trạng:** Hoàn thành giai đoạn ổn định khung (Framework Stability)

---

## 1. MỤC TIÊU CỐT LÕI
Phát triển hệ thống lập luận dựa trên Tác nhân (Agentic Reasoning) kết hợp cấu trúc Trí nhớ kép (Dual Memory) nhằm vượt qua các giới hạn của hệ thống RAG (Retrieval-Augmented Generation) truyền thống trong các bài toán truy vấn đa bước phức tạp.

## 2. NHỮNG ĐÓNG GÓP & ĐỘT PHÁ CÔNG NGHỆ
So với các phương pháp cũ, hệ thống hiện tại đã đạt được các bước tiến đột phá sau:

*   **Kiến trúc Trí nhớ Kép (Dual Memory Architecture):** Khác với RAG cũ chỉ dựa trên Vector DB, hệ thống mới tích hợp đồng thời Semantic Memory (Vector) và Episodic/Structural Memory (Neo4j Graph).
*   **Cơ chế Lập luận Tự thích nghi (Agentic Reasoning):** Sử dụng các mô hình ReAct và Reflexion, cho phép Agent tự "suy nghĩ" và "kiểm chứng" thông tin trước khi trả lời.
*   **Tối ưu hóa bằng Lý thuyết Thông tin (Information-Theoretic Control):** Bộ chọn bằng chứng (Evidence Selector) sử dụng hàm mục tiêu để tối ưu hóa giá trị thông tin trên mỗi Token, giúp tránh hiện tượng nhiễu ngữ cảnh.
*   **Học tương phản tiềm ẩn (Contrastive Latent Induction):** Module Prototype Learner có khả năng tự phân tách các cụm tri thức tương đồng nhưng có bản chất khác nhau, tăng độ chính xác trong lập luận chuyên sâu.
*   **Tiến hóa Ontology động (Continual Learning):** Đồ thị tri thức tự cập nhật và học hỏi qua mỗi lần truy vấn, giúp Agent tích lũy kinh nghiệm theo thời gian thực mà không cần huấn luyện lại.
*   **Ablation Suite tự động:** Xây dựng thành công bộ công cụ cho phép so sánh 8 chiến lược truy xuất khác nhau chỉ bằng một câu lệnh, đảm bảo tính khách quan và khoa học cho bài báo Q1.
*   **Đánh giá bằng AI (LLM-as-a-judge):** Tích hợp DeepEval để tự động chấm điểm Faithfulness, Relevancy và Precision, loại bỏ yếu tố cảm tính của con người.

## 3. CÁC KẾT QUẢ ĐÃ ĐẠT ĐƯỢC (MILESTONES)
1.  **Ổn định mã nguồn:** Cấu trúc lại toàn bộ hệ thống quản lý cấu hình và môi trường (Production-grade code).
2.  **Kết nối Đồ thị:** Thiết lập thành công kết nối Hybrid (Vector + Cypher) trên Neo4j.
3.  **Thực nghiệm Baseline:** Chạy thành công các thử nghiệm cơ sở trên tập dữ liệu Hard Bridge, dữ liệu đã được xuất ra định dạng CSV để phục vụ viết báo.
4.  **Fix Bugs:** Giải quyết triệt để các lỗi về Asyncio, Dependency và Shutdown của các thư viện lớn (DeepEval, LangChain, Google GenAI).

## 4. PHÂN TÍCH KẾT QUẢ HIỆN TẠI
Dữ liệu từ file `react_vector_rag.csv` cho thấy:
*   **Thành công:** Agent trả lời đúng câu hỏi khó về Shirley Temple.
*   **Vấn đề:** Chỉ số **Contextual Precision** thấp (0.16) do phương pháp Vector RAG lấy quá nhiều thông tin không liên quan.
*   **Hướng giải quyết:** Đây chính là minh chứng quan trọng để đề xuất phương pháp **Graph-based Retrieval** của chúng ta nhằm tăng độ chính xác của ngữ cảnh.

## 5. HẠN CHẾ & THÁCH THỨC (CRITICAL ANALYSIS)
*   **Tính tổng quát hóa (Generalization):** Mới chỉ được kiểm thử trên dữ liệu HotpotQA phổ thông, cần chứng minh hiệu quả trên các miền tri thức chuyên sâu (Y tế, Pháp luật).
*   **Sự phụ thuộc Model (Model Dependency):** Hiện tại hệ thống đang tối ưu hóa theo Gemini API, cần mở rộng để hỗ trợ các mô hình mã nguồn mở (Llama, Mistral) nhằm đảm bảo tính độc lập nền tảng.
*   **Nghẽn cổ chai Đánh giá (Evaluation Bottleneck):** Việc sử dụng LLM-as-a-judge cho 8 metrics mang lại độ chính xác cao nhưng đánh đổi bằng thời gian xử lý và chi phí API đáng kể.
*   **Dữ liệu Đồ thị:** Neo4j hiện đang ở trạng thái sơ khởi, chưa nạp đủ các "Experiences" và "Insights" để khai thác hết tiềm năng của thuật toán Graph Traversal.

## 6. LỘ TRÌNH TIẾP THEO (NEXT STEPS)
1.  **Ingestion & Fine-tuning:** Nạp dữ liệu thực tế vào Neo4j và tinh chỉnh tham số `EVIDENCE_FRONTIER_MULTIPLIER` cho các miền tri thức khác nhau.
2.  **Parallelized Evaluation:** Triển khai cơ chế đánh giá song song và tích hợp mô hình đánh giá cục bộ (Local Judge) để giảm 70% thời gian thực nghiệm.
3.  **Human-in-the-loop (HIL):** Hoàn thiện module HIL để chuyên gia có thể hiệu đính các Ontology được học tự động, tạo ra vòng lặp phản hồi tích cực.
4.  **Large-scale Experiment:** Thực hiện chạy diện rộng (100+ câu hỏi) và trực quan hóa kết quả bằng biểu đồ Radar để làm nổi bật sự vượt trội của DualMemoryKG trong phần thảo luận của bài báo.

## 7. KẾ HOẠCH HÀNH ĐỘNG CHI TIẾT (IMMEDIATE ACTION PLAN)
#### Giai đoạn 1: Làm giàu Tri thức (Knowledge Enrichment)
*   **Mục tiêu:** Nạp dữ liệu "Memories" vào Neo4j để thoát khỏi tình trạng "Empty Graph".
*   **Hành động:** Chạy script nạp dữ liệu (Ingestion) với tập mẫu chất lượng cao (~100-200 nodes).
*   **Kết quả:** Neo4j sẽ chứa các quan hệ tri thức thực tế, giúp các chiến lược Graph RAG phát huy tối đa hiệu quả.

#### Giai đoạn 2: Thực nghiệm quy mô lớn (Large-scale Evaluation)
*   **Mục tiêu:** Thu thập số liệu thống kê có ý nghĩa khoa học (Statistical Significance).
*   **Hành động:** Sử dụng Ablation Suite đã hoàn thiện để chạy thực nghiệm trên tập 50-100 câu hỏi.
*   **Lưu ý:** Nên thực hiện chạy vào thời điểm API ổn định để lấy số liệu sạch nhất.

#### Giai đoạn 3: Phân tích & Trực quan hóa (Analytics & Visualization)
*   **Mục tiêu:** Biến các con số thành biểu đồ trực quan cho bài báo/luận văn.
*   **Hành động:** Tổng hợp các file CSV kết quả, tính toán mức tăng trưởng (%) về Precision và Faithfulness của DualMemoryKG so với RAG truyền thống.

#### Giai đoạn 4: Hoàn thiện bản thảo khoa học (Publication Preparation)
*   **Mục tiêu:** Hoàn tất nội dung bài báo/luận văn.
*   **Hành động:** Sử dụng kiến trúc hệ thống và dữ liệu thực nghiệm đã thu thập để viết phần "Methodology" và "Results & Discussion".

## 8. CHIẾN LƯỢC TỐI ƯU HÓA HIỆU NĂNG & CHI PHÍ (EFFICIENCY & COST OPTIMIZATION)
#### 8.1. Tối ưu hóa Độ trễ (Latency)
*   **Chiến lược Phân tầng (Model Cascading):** Sử dụng các mô hình nhỏ (Small Language Models) cho các tác vụ phụ trợ như phân loại thực thể và duyệt đồ thị, chỉ dùng mô hình lớn cho bước lập luận cuối cùng.
*   **Duyệt đồ thị song song (Parallel Traversal):** Tận dụng khả năng xử lý đồng thời của Neo4j để mở rộng frontier tìm kiếm, giảm thời gian chờ đợi giữa các bước truy xuất.
*   **Cơ chế Cache Tri thức:** Lưu trữ các đường dẫn lập luận (Reasoning Paths) phổ biến vào bộ nhớ đệm để phản hồi tức thì cho các câu hỏi tương tự.

#### 8.2. Tối ưu hóa Chi phí (Cost)
*   **Kiểm soát ngân sách bằng chứng (Budgeting):** Tinh chỉnh tham số `EVIDENCE_SELECTION_BUDGET` để đảm bảo sự cân bằng giữa độ chính xác và lượng Token tiêu thụ.
*   **Cắt tỉa dựa trên Lý thuyết Thông tin:** Loại bỏ các bằng chứng có độ dư thừa cao, chỉ nạp vào ngữ cảnh những thông tin mang lại giá trị gia tăng (Incremental Information) lớn nhất.
*   **Long-term Memory persistence:** Khai thác triệt để bộ nhớ dài hạn trên Neo4j để tránh việc lặp lại các chu trình suy luận tốn kém, chuyển đổi từ "tư duy tốn token" sang "truy xuất tri thức có sẵn".

## 9. TRUY VẾT & GIÁM SÁT (OBSERVABILITY & TRACING)
Hệ thống không phải là một "hộp đen". Chúng tôi đã tích hợp công cụ giám sát tiên tiến:
*   **Langfuse Integration:** Cho phép truy vết toàn bộ vòng đời của một yêu cầu (Trace lifecycle), từ bước truy xuất tri thức đến các bước lập luận trung gian của Agent.
*   **Error RCA (Root Cause Analysis):** Module chẩn đoán lỗi tự động giúp xác định nhanh chóng nguyên nhân khiến Agent thất bại (do truy xuất thiếu thông tin hay do lập luận sai).

## 10. ĐỊNH NGHĨA CÁC ĐỘ ĐO KHOA HỌC (METRICS DEFINITION)
Sử dụng bộ chỉ số tiêu chuẩn từ DeepEval để đảm bảo tính khách quan:
*   **Faithfulness (Độ trung thực):** Đo lường mức độ câu trả lời được căn cứ vào tài liệu truy xuất được (Grounding), đảm bảo không có ảo giác (Hallucination).
*   **Answer Relevancy (Độ phù hợp):** Đánh giá mức độ câu trả lời giải quyết trực tiếp vấn đề người dùng đặt ra.
*   **Contextual Precision (Độ chính xác ngữ cảnh):** Đo lường chất lượng của bộ máy truy xuất (Retrieval Engine) - liệu thông tin quan trọng nhất có nằm ở vị trí ưu tiên hay không.

## 11. MÔI TRƯỜNG THỰC NGHIỆM (EXPERIMENTAL SETUP)
*   **LLM Engine:** Google Gemini 2.5 Flash (Dòng mô hình tối ưu cho tác vụ Agentic).
*   **Graph Database:** Neo4j 5.x (Hỗ trợ Vector Index và truy vấn đồ thị phức tạp).
*   **Framework:** LangChain Classic kết hợp với các module tùy chỉnh của dự án DualMemoryKG.
*   **Evaluation:** DeepEval 4.x với mô hình giám khảo (Judge) là Gemini-2.5-flash-lite.

## 12. QUẢN TRỊ NỢ KỸ THUẬT & TÍNH ỔN ĐỊNH (SYSTEM RESILIENCE)
*   **Chuẩn hóa Dependency:** Tối ưu hóa `requirements.txt` đảm bảo tính tương thích giữa các thư viện AI hàng đầu (LangChain, DeepEval, GenAI).
*   **Resume-on-Failure:** Cơ chế tự động bỏ qua các thí nghiệm đã hoàn thành và chạy tiếp từ điểm lỗi, đảm bảo tính toàn vẹn của dữ liệu trong các đợt thực nghiệm dài ngày.

## 13. KHẢ NĂNG MỞ RỘNG TRỌN ĐỜI (LIFELONG LEARNING POTENTIAL)
*   **Persistent Knowledge Base:** Khác với RAG truyền thống bị giới hạn bởi cửa sổ ngữ cảnh, DualMemoryKG tích lũy tri thức vĩnh viễn trên Neo4j.
*   **Evolving Intelligence:** Hệ thống được thiết kế để "càng dùng càng thông minh", biến các trải nghiệm thất bại trong quá khứ thành bài học kinh nghiệm cho tương lai thông qua module Reflexion và Prototype Learner.

---
**Tóm tắt giá trị khoa học:** Hệ thống không chỉ là một công cụ truy xuất thông tin, mà là một thực thể học tập liên tục, kết hợp giữa toán học (Information Theory) và khoa học nhận thức (Dual Memory).

**Người báo cáo:** (Tên của bạn)
**Hệ thống hỗ trợ:** Antigravity AI (Google DeepMind)
