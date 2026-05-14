# Tài liệu Báo cáo Tiến độ Nghiên cứu Chiến lược (Chuẩn Q1)
## Dự án: DualMemoryKG - Sự đột phá so với các kiến trúc truyền thống

---

### PHẦN 1: ĐẶT VẤN ĐỀ VÀ GIỚI HẠN CỦA PHƯƠNG PHÁP CŨ

#### Slide 1: Bối cảnh Nghiên cứu
- **Tiêu đề:** DualMemoryKG - Nâng cấp năng lực suy luận có căn cứ cho LLM.
- **Sứ mệnh:** Chuyển đổi từ hệ thống "Truy xuất thông thường" sang "Điều khiển suy luận thông minh".

#### Slide 2: Giới hạn của các hệ thống RAG/Agent hiện nay (The Baselines)
- **Hệ thống cũ:** Chỉ có 1 loại bộ nhớ (văn bản), dựa trên tìm kiếm tương đồng (Similarity), dễ mắc lỗi ảo giác và không ổn định khi thay đổi lĩnh vực.
- **Hệ thống của chúng ta:** Xây dựng một Stack suy luận 4 tầng để khắc phục triệt để các giới hạn này.

---

### PHẦN 2: CHI TIẾT CÁC CẢI TIẾN VÀ ĐÓNG GÓP KHOA HỌC (BEFORE VS AFTER)

#### Slide 3: Contribution 1 - Đột phá về Cấu trúc dữ liệu (Representation Upgrade)
- **Ban đầu (Baseline):** Single Semantic Memory (Chỉ lưu trữ văn bản tĩnh). 
  - *Hệ quả:* Tác tử thường lặp lại sai lầm vì không nhớ được quá trình thực thi.
- **DualMemoryKG (Cải tiến):** Unified Meta-Schema (Facts ⊕ Traces).
  - *Đột phá:* Tác tử có khả năng "Liên tưởng kinh nghiệm". Nó biết mẩu tin này đã từng dẫn đến sai lầm nào trong quá khứ.

#### Slide 4: Contribution 2 - Đột phá về Nhận thức (Cognitive Upgrade)
- **Ban đầu (Baseline):** Fixed Schema / Manual Tagging (Gán nhãn thủ công hoặc quy tắc cứng).
  - *Hệ quả:* Kém linh hoạt khi sang lĩnh vực mới (ví dụ từ Y sang Luật).
- **DualMemoryKG (Cải tiến):** Adaptive Ontology Induction.
  - *Đột phá:* Hệ thống **Tự suy diễn mẫu suy luận** mà không cần con người can thiệp.
  - **Visible Formula:** `P(Concept | Trace) = Softmax(-dist(x, Prototype))`

#### Slide 5: Contribution 3 - Đột phá về Điều phối (Control Upgrade)
- **Ban đầu (Baseline):** Heuristic Similarity (Truy xuất dựa trên độ tương đồng bề mặt).
  - *Hệ quả:* LLM bị "ngập" trong bằng chứng dư thừa và gây nhiễu (Irrelevant context).
- **DualMemoryKG (Cải tiến):** Information-Theoretic Evidence Control.
  - *Đột phá:* Chỉ chọn bằng chứng có **Lợi ích thông tin (Utility)** cao nhất.
  - **Visible Formula:** `Utility = Information_Gain - Penalty_Redundancy`

#### Slide 6: Contribution 4 - Đột phá về Kiểm chứng (Safety Upgrade)
- **Ban đầu (Baseline):** Empirical Evaluation (Đánh giá dựa trên cảm tính hoặc tỷ lệ F1 đơn thuần).
  - *Hệ quả:* Không có đảm bảo toán học, hệ thống vẫn "hên xui".
- **DualMemoryKG (Cải tiến):** Lipschitz-Stable Verification.
  - *Đột phá:* Cung cấp **Chứng minh toán học** đầu tiên về tính ổn định của suy luận có căn cứ.
  - **Visible Formula:** `Δ_Output ≤ K * Δ_Evidence`

#### Slide 7: Tóm tắt Sự nhảy vọt về Công nghệ (The Breakthrough Summary)
| Tính năng | Hệ thống truyền thống | DualMemoryKG (Của chúng ta) |
| :--- | :--- | :--- |
| **Loại bộ nhớ** | Tĩnh (Semantic) | Tĩnh + Động (Dual-Memory) |
| **Cơ chế hiểu** | Quy tắc cứng (Heuristik) | Tự học (Adaptive Ontology) |
| **Logic chọn lọc** | Độ tương đồng (Similarity) | Tiện ích thông tin (Utility) |
| **Độ tin cậy** | Chỉ số thực nghiệm | Đảm bảo toán học (Lipschitz) |

---

### PHẦN 3 & 4: KẾT QUẢ THỰC NGHIỆM VÀ ROADMAP Q1
*(Các slide này tập trung vào số liệu thực tế chứng minh sự vượt trội của DualMemoryKG trên các tập dữ liệu khó như HotpotQA và HaluEval)*

---
**Gợi ý cho bạn:** Khi thuyết trình Slide 7, hãy dùng bảng so sánh này để "chốt hạ" với Giáo sư. Đây là bằng chứng rõ nhất cho thấy khối lượng công việc và sự sáng tạo mà bạn đã bỏ vào nghiên cứu.
