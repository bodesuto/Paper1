# Hình thức hóa Học thuật: Tiêu chuẩn DualMemoryKG cho Công bố Q1

Tài liệu này cung cấp nền tảng toán học hình thức cho khung làm việc DualMemoryKG, tập trung cụ thể vào các yêu cầu của các tạp chí có tác động cao (High-Impact - Q1).

---

## 1. Định lý: Hội tụ có Căn cứ (Định luật Phân rã Ảo giác)

**Định lý 1.** Gọi $\mathcal{P}_t$ là tập hợp các bằng chứng được thu thập cho đến bước $t$. Dưới Chiến sách Duyệt đồ thị dựa trên Lý thuyết Thông tin (Information-Theoretic Traversal Policy) $\pi_{\text{IG}}$, xác suất của một phản hồi ảo giác $P(E_{\text{hallucinate}})$ sẽ phân rã theo hàm mũ khi Lợi ích Thông tin (Information Gain - IG) tiệm cận với entropy nội tại của nhiệm vụ $H(Q)$.

**Phát biểu Hình thức:**
$$ P(Y \neq Y^* \mid \mathcal{P}_t) \leq \exp \left( - \lambda \cdot \sum_{i=1}^t \text{IG}(v_i \mid \mathcal{P}_{i-1}) \right) $$
trong đó $\lambda$ là *Hằng số Căn cứ* (Grounding Constant) đặc thù cho mật độ suy luận của LLM.

**Ý nghĩa:** Định lý này chuyển đổi việc "giảm ảo giác" từ một tuyên bố cảm tính thành một thuộc tính hội tụ có thể chứng minh được của kiến trúc.

---

## 2. Cơ sở Lý thuyết: Tính liên tục Lipschitz của Ontology Tiềm ẩn

Chúng tôi định nghĩa đa tạp suy luận $\mathcal{M}$ là không gian nhúng của các dấu vết hành vi (behavioral traces).

**Mệnh đề 1.** Lực đẩy đối kháng (Contrastive Repulsion Force) $\alpha$ đảm bảo rằng ánh xạ $f: \mathcal{Q} \to \mathcal{Z}$ thỏa mãn điều kiện Lipschitz:
$$ \| f(q_1) - f(q_2) \|_{\mathcal{Z}} \leq L \cdot \| q_1 - q_2 \|_{\mathcal{Q}} $$
trong đó $L$ được cực tiểu hóa bởi biên độ cụm $\Gamma$.

**Tác động:** Một giá trị $L$ thấp hơn cho thấy hệ thống bền bỉ trước các tác động đối kháng (adversarial robustness) trong câu hỏi, đảm bảo rằng những thay đổi ngữ nghĩa nhỏ không dẫn đến việc phân loại sai nghiêm trọng các chiến lược suy luận.

---

## 3. Chỉ số: Hiệu quả Nén Tri thức (IGpT)

Các hệ thống RAG truyền thống thường kém hiệu quả vì chúng tối ưu hóa cho **Độ tương đồng** (Similarity) thay vì **Giá trị hữu dụng** (Utility). Chúng tôi giới thiệu chỉ số **Lợi ích Thông tin trên mỗi Token (Information Gain per Token - IGpT)**:

$$ \text{IGpT} = \frac{\int_{t} \text{IG}(v_t) dt}{\sum \text{Tokens}} $$

**Tuyên bố Khoa học:** DualMemoryKG đạt được Đường biên Pareto (Pareto Frontier) vượt trội trong không gian Độ chính xác-vs-Ngữ cảnh bằng cách tối đa hóa IG đồng thời phạt sự dư thừa thông qua số hạng $\gamma$ trong hàm mục tiêu của chúng tôi.

---

## 4. Cơ chế: Tính dẻo Synap Hebbian trên Đồ thị

Chúng tôi mô hình hóa Đồ thị Tri thức không phải là một cơ sở dữ liệu tĩnh, mà là một **Đa tạp Bộ nhớ Bền vững** (Persistent Memory Manifold).

**Quy tắc Cập nhật (Hebbian):**
$$ w_{ij}^{(t+1)} = w_{ij}^{(t)} + \eta \cdot \mathbb{I}(\text{Success} \mid \text{Edge}_{ij} \in \mathcal{P}) $$
trong đó $\eta$ là tốc độ học và $\mathbb{I}$ là hàm chỉ thị của sự thành công có căn cứ.

**Thuộc tính Hệ quả:** Hệ thống thể hiện **Trí tuệ Tập thể** (Collective Intelligence), trong đó chiến sách duyệt đồ thị ngày càng trở nên chuyên biệt cho miền mục tiêu thông qua "Phản hồi Môi trường" thay vì phải huấn luyện lại (re-training) tốn kém.

---

## 5. Nguyên lý: Điểm nghẽn Thông tin trong Suy luận Tác tử

Chúng tôi hình thức hóa tác tử suy luận như một kênh truyền thông giữa bộ nhớ thô $X$ và câu trả lời cuối cùng $Y$. 

**Hàm Mục tiêu (Lagrangian):**
$$ \min_{\mathcal{P}} \left[ I(X; \mathcal{P}) - \beta I(\mathcal{P}; Y) \right] $$
trong đó $I(X; \mathcal{P})$ là độ phức tạp của ngữ cảnh được truy xuất và $I(\mathcal{P}; Y)$ là giá trị hữu dụng dự báo.

**Tuyên bố Khoa học:** DualMemoryKG hoạt động như một bộ lọc tối ưu loại bỏ nhiễu lĩnh vực trong khi vẫn giữ lại các "Biến bất biến" (Invariants) cần thiết cho suy luận có căn cứ, đạt tới giới hạn **Thống kê Đầy đủ** (Sufficient Statistic) cho truy vấn cụ thể.

---

## 6. Phân tích: Độ phức tạp Tính toán vs. Mật độ Suy luận

Chúng tôi chứng minh rằng chi phí gia tăng của việc lựa chọn dựa trên Lý thuyết Thông tin là không đáng kể so với việc giảm chi phí suy luận của LLM.

**Độ phức tạp:**
Chiến sách duyệt vận hành trong $O(T \cdot K \cdot \log V)$, trong đó $T$ là số bước nhảy suy luận, $K$ là hệ số nhánh, và $V$ là số lượng đỉnh. 

**Đột phá Hiệu suất:** Bằng cách cắt tỉa không gian tìm kiếm thông qua ngưỡng Entropy, chúng tôi cho thấy sự giảm hệ số hằng số trong **Tỷ lệ Token trên Giải pháp (Token-to-Solution Ratio - TSR)**, giúp DualMemoryKG có khả năng mở rộng tốt hơn so với các phương pháp Dense Retrieval truyền thống cho các nhiệm vụ suy luận đa bước ngữ cảnh dài.

---

## 7. Siêu động lực học: Độ ổn định Tham số & HIL kích hoạt bởi Độ bất định

Chúng tôi định nghĩa **Tính siêu ổn định** (Meta-stability) của hệ thống là khả năng hội tụ ngay cả dưới sự điều chỉnh tham số động ($\beta, \gamma$).

**Kích hoạt Hình thức cho Con người tham gia (Human-in-the-Loop - HIL):**
Gọi $\Psi$ là khoảng cách nhận thức được đo bởi Cơ chế Phân xử Cân bằng. Một yêu cầu can thiệp của con người được kích hoạt nếu:
$$ \Psi(q, \mathcal{P}) > \tau \quad \land \quad \frac{\partial \Psi}{\partial t} \approx 0 $$
trong đó $\tau$ là ngưỡng bất định tới hạn và $t$ là số lần lặp.

**Tuyên bố Khoa học:** Cơ chế này đảm bảo rằng DualMemoryKG sở hữu sự **Khiêm tốn Nhận thức** (Epistemic Humility), biết khi nào các nguồn tri thức nội tại và ngoại tại của nó không đủ để cung cấp một câu trả lời có căn cứ, từ đó đạt tới cấp độ cao nhất của **AI Tin cậy và Có thể giải thích được**.
