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

### Đột phá 1: Contrastive Latent Ontology Induction (Học Ontology Tiềm Ẩn Đối Kháng)
Thay vì dùng các nhãn phân loại tĩnh (static labels) dễ gãy nứt khi chuyển đổi Domain, hệ thống tự động học các "Chiến thuật Suy luận" từ dấu vết dữ liệu. 

**Cơ chế:** Prototype của mỗi Concept $c_k$ được cập nhật bằng cách cộng dồn các vector thành công và **trừ đi Lực đẩy (Repulsion Vector)** từ các concept đối lập.
$$ c_k = \text{Norm} \left( \sum_{i \in S_k} w_i v_i + \alpha \cdot \text{Repulsion}(c_k, \mathcal{C}_{neg}) \right) $$

*Luận điểm Q1:* Việc này chứng minh bằng toán học rằng mô hình chủ động "mở rộng lề" (margin) giữa các chiến thuật suy luận, giúp Agent phân biệt rõ ràng cách xử lý các câu hỏi đa nghĩa.

### Đột phá 2: Information-Theoretic Evidence Selection (Chọn Bằng Chứng Dựa Trên Lý Thuyết Thông Tin)
RAG truyền thống chọn tài liệu dựa trên độ tương đồng (Cosine Similarity). Hệ thống này chọn bằng chứng dựa trên **Lợi Ích Thông Tin Biên (Marginal Information Gain)**.

**Cơ chế:**
Mỗi Node mới được thêm vào tập $\mathcal{P}$ sẽ được đánh giá qua hàm:
$$ \Delta \mathcal{U}(v) = \text{Sim}(v, z(q)) + \beta \cdot IG(v | \mathcal{P}_t) - \gamma \cdot \text{Redundancy}(v, \mathcal{P}_t) $$

*Luận điểm Q1:* Chúng ta trừng phạt sự dư thừa (Redundancy Penalty) và ưu tiên giảm độ bất định (Entropy Reduction). Điều này đảm bảo LLM nhận được một ngữ cảnh rộng nhất, đa dạng nhất với số lượng Token ít nhất.

### Đột phá 3: Deep Error Decomposition Framework (Khung Phân Tích Lỗi Sâu)
Hệ thống chẩn đoán lỗi (RCA) sử dụng một Taxonomy mang tính khoa học cao:
*   **E-Ont (Ontology Mismatch):** Sai lệch do chọn nhầm chiến thuật suy luận.
*   **E-Trav (Traversal Suboptimality):** Đi sai đường trên Đồ thị Tri thức.
*   **E-Gnd (Grounding Gap):** Có bằng chứng nhưng LLM vẫn sinh ra ảo giác.
*   **E-KB (Knowledge Deficiency):** Lỗ hổng tri thức gốc.
*   **E-Loop (Reasoning Loop):** Bị kẹt trong vòng lặp tư duy.

*Luận điểm Q1:* Bằng cách phân tách chính xác nguyên nhân lỗi thay vì chỉ báo cáo "Độ chính xác" (Accuracy), bài báo chứng minh được sự minh bạch (Interpretability) và tính kiểm soát (Controllability) của toàn bộ kiến trúc.

---

## 3. Kiến Trúc Cấu Trúc Sản Phẩm (Production-Ready Architecture)

Hệ thống không chỉ là một kịch bản thử nghiệm (scripting) mà đã được đóng gói chuẩn Kỹ nghệ Phần mềm (Software Engineering Standard):

1.  **Pydantic Configuration:** Quản lý môi trường tập trung, Fail-fast và tự động kiểm tra kiểu dữ liệu (Type Validation), sẵn sàng tích hợp với FastAPI/Kubernetes.
2.  **Modular Packaging (`pyproject.toml`):** Toàn bộ hệ thống có thể được cài đặt như một thư viện Python độc lập.
3.  **Strict Linting:** Áp dụng Black, isort, và Mypy để đảm bảo chất lượng code ngang tầm hệ thống doanh nghiệp (Enterprise).

Tất cả những yếu tố này khẳng định: **Đây là một nền tảng (Framework) có thể chuyển giao và mở rộng, không phải là một đồ án nghiên cứu nhỏ lẻ.**
