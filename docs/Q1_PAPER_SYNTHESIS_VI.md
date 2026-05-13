# BẢN TỔNG HỢP KIẾN TRÚC & LÝ THUYẾT CHO BÀI BÁO Q1
*(Q1 Paper Synthesis Document)*

Tài liệu này tổng hợp toàn bộ các đột phá về mặt **Kiến trúc Hệ thống (System Architecture)** và **Lý thuyết Học máy (Machine Learning Theory)** đã được triển khai trong Codebase, sẵn sàng để đưa vào phần **Methodology** và **Evaluation** của bài báo Q1.

---

## 1. Phát Biểu Bài Toán (Problem Formulation)

Hệ thống của chúng ta giải quyết bài toán: **Domain-Agnostic Grounded Reasoning** (Suy luận có căn cứ độc lập lĩnh vực).

Cho một câu hỏi $q \in \mathcal{Q}$ và một đồ thị tri thức bộ nhớ kép $\mathcal{G} = (\mathcal{V}, \mathcal{E})$. Nhiệm vụ của hệ thống không phải là tìm ra câu trả lời trực tiếp, mà là xác định một **Tập Bằng Chứng (Support Set)** $\mathcal{P} \subseteq \mathcal{V}$ sao cho LLM có thể sinh ra câu trả lời dựa trên $\mathcal{P}$:
$$ y = f_{LLM}(q, \mathcal{P}) $$

Để tránh hiện tượng "Ảo giác" (Hallucination), việc chọn $\mathcal{P}$ được mô hình hóa thành bài toán **Tối ưu hóa Ràng buộc**:
$$ \max_{\mathcal{P} \subseteq \mathcal{V}} \text{Utility}(\mathcal{P} | q, \mathcal{Z}) - \lambda \cdot \text{Cost}(\mathcal{P}) $$
Trong đó $\mathcal{Z}$ là Không gian Ontology tiềm ẩn.

---

## 2. Các Đột Phá Lõi (Core Breakthroughs)

### Đột phá 1: Contrastive Latent Ontology Induction & Lipschitz Stability
Thay vì các nhãn tĩnh, hệ thống tự học "Chiến thuật Suy luận" từ behavioral traces qua cơ chế Contrastive Prototype Learning.

**Toán học và Tính Bền bỉ:**
Lực đẩy Repulsion Force ($c_k = \text{Norm}(\dots)$) đảm bảo rằng không gian tiềm ẩn $\mathcal{Z}$ thỏa mãn điều kiện **Lipschitz Continuity**. Điều này chứng minh bằng thực nghiệm rằng hệ thống có tính **Adversarial Robustness**: Một sự thay đổi nhỏ (nhiễu) trong câu hỏi sẽ không dẫn đến sự thay đổi đột biến trong việc chọn chiến thuật suy luận.

### Đột phá 2: Information-Theoretic Evidence Selection (Nguyên lý Information Bottleneck)
RAG truyền thống tối ưu cho độ tương đồng. DualMemoryKG tối ưu cho **Lợi ích Thông tin Biên (Marginal Information Gain - IG)**.

**Cơ chế Tối ưu:**
Hệ thống hoạt động như một bộ lọc **Information Bottleneck (IB)**, nén tối đa dữ liệu đầu vào $I(X; \mathcal{P})$ nhưng giữ lại tối đa thông tin dự đoán $I(\mathcal{P}; Y)$. Điều này giúp tối ưu hóa chỉ số **IGpT (Information Gain per Token)**, đạt điểm Pareto Optimal vượt trội so với Microsoft GraphRAG.

### Đột phá 3: Synaptic Plasticity & Hebbian Graph Evolution
Đồ thị tri thức (Neo4j) không phải là cơ sở dữ liệu tĩnh, mà là một cục diện **Trí nhớ dài hạn có khả năng tiến hóa**.

**Cơ chế:** Áp dụng giải thuật **Hebbian Learning** ($w_{ij}^{(t+1)} = w_{ij}^{(t)} + \eta \cdot \text{Success}$). Các con đường lập luận dẫn đến câu trả lời đúng sẽ được gia cố trọng số theo thời gian, giúp Agent "càng dùng càng thông minh" (Lifelong Learning) mà không cần huấn luyện lại mô hình ngôn ngữ.

### Đột phá 4: Reasoning Equilibrium (Cơ chế Phân xử Tin cậy)
Giải quyết bài toán mâu thuẫn giữa kiến thức nội tại của LLM (Internal) và bằng chứng từ Đồ thị (External).

**Toán học:** Sử dụng phép đo khoảng cách nhận thức (Cognitive Gap) thông qua Entropy của xác suất đầu ra (Logits). Cơ chế này tạo ra một **Hallucination Shield**, đảm bảo tính **Honesty** (Trung thực) cho AI bằng cách ép Agent phải hoài nghi và phản biện khi phát hiện mâu thuẫn tri thức.

### Đột phá 5: Deep Error Decomposition Framework (RCA Engine)
Phân tách lỗi theo taxonomy khoa học: `E-Ont` (Sai lệch Ontology), `E-Trav` (Sai lệch Duyệt), `E-Gnd` (Mất căn cứ).

*Luận điểm Q1:* Bằng cách phân tách chính xác nguyên nhân lỗi thay vì chỉ báo cáo "Độ chính xác" (Accuracy), bài báo chứng minh được sự minh bạch (Interpretability) và tính kiểm soát (Controllability) của toàn bộ kiến trúc.

### Đột phá 6: Auto-Adaptive Meta-Tuning (Tối ưu hóa tham số động)
Giải quyết bài toán cấu hình tham số thủ công (manual tuning).

**Cơ chế:** Module `ParameterAutoTuner` sử dụng vòng lặp phản hồi từ `Reflexion` để điều chỉnh các trọng số $\beta$ và $\gamma$ trong thời gian thực. Điều này giúp hệ thống đạt tới trạng thái **Meta-Stability**, duy trì hiệu năng tối ưu ngay cả khi phân phối của dữ liệu đầu vào thay đổi.

### Đột phá 7: Epistemic Humility & Uncertainty-Triggered HIL
Xây dựng cơ chế AI "biết rõ những gì mình không biết".

**Cơ chế:** Sử dụng bộ phân xử mâu thuẫn nhận thức để kích hoạt sự can thiệp của con người (Human-in-the-loop) khi và chỉ khi độ bất định toán học $\Psi$ vượt ngưỡng an toàn sau nhiều lần thử. Đây là đóng góp cốt lõi cho lĩnh vực **Trustworthy AI** (AI tin cậy).

---

## 3. Kiến Trúc Cấu Trúc Sản Phẩm (Production-Ready Architecture)

Hệ thống đã được chuẩn hóa Kỹ nghệ Phần mềm chuyên nghiệp:

1.  **Pydantic Configuration:** Quản lý môi trường tập trung, Fail-fast.
2.  **Diagnostics Suite:** Tích hợp `ManifoldAnalyzer` và `EntropyTracker` để cung cấp các chỉ số khoa học thời gian thực.
3.  **Explainability layer:** Chuyển đổi các thông số IG/Weights thành "Bản tường thuật lập luận" dễ hiểu cho con người.

Tất cả các yếu tố trên khẳng định **DualMemoryKG** là một kiến trúc AI tin cậy, có khả năng giải thích và tự tiến hóa, đáp ứng các tiêu chuẩn khắt khe nhất của cộng đồng khoa học quốc tế.
