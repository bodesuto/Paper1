# HƯỚNG DẪN CHẠY HỆ THỐNG DUALMEMORYKG (STEP-BY-STEP)

> [!IMPORTANT]
> Đối với quy trình thực nghiệm quy mô lớn (10,000 câu hỏi) đã được tối ưu hóa cho bài báo Q1, vui lòng tham khảo: [**EXPERIMENT_GUIDE_V2.md**](../EXPERIMENT_GUIDE_V2.md)

Tài liệu này hướng dẫn bạn từ lúc bắt đầu cho đến khi ra được kết quả nghiên cứu cuối cùng.

---

## Bước 1: Chuẩn bị môi trường

1.  **Cài đặt Python:** Đảm bảo bạn dùng Python 3.9 trở lên.
2.  **Cài đặt Neo4j:**
    *   Sử dụng Neo4j Desktop hoặc Neo4j Aura (Cloud).
    *   Ghi lại: `URI`, `Username`, và `Password`.
3.  **API Keys:**
    *   Cần `GOOGLE_API_KEY` (cho Gemini).
    *   (Tùy chọn) `LANGFUSE_PUBLIC_KEY` & `LANGFUSE_SECRET_KEY` nếu muốn theo dõi Trace.

---

## Bước 2: Cài đặt thư viện

Mở terminal tại thư mục gốc của dự án và chạy:

```bash
# Tạo môi trường ảo (Khuyên dùng)
python -m venv venv
source venv/bin/activate  # Trên Windows dùng: venv\Scripts\activate

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# Cài đặt dự án ở chế độ Editable (để các module nhận diện được nhau)
pip install -e .
```

---

## Bước 3: Cấu hình biến môi trường (`.env`)

1.  Copy file mẫu: `cp .env.example .env` (hoặc đổi tên file thủ công).
2.  Mở file `.env` và điền đầy đủ thông tin:
    *   `GOOGLE_API_KEY=...`
    *   `NEO4J_URI=bolt://localhost:7687`
    *   `NEO4J_PASSWORD=...`

---

## Bước 4: Chạy thử nghiệm nhanh (Smoke Test)

Trước khi chạy thí nghiệm lớn tốn phí API, hãy chạy thử để kiểm tra kết nối:

```bash
# Kiểm tra Agent ReAct đơn thuần (không cần Neo4j)
python scripts/run_react_smoke.py --limit 3

# Kết quả sẽ được lưu tại: eval/data/react_smoke_results.csv
```

---

## Bước 5: Thí nghiệm Khoa học Cấp cao (Elite Research Pipeline)

Đây là quy trình tối ưu cho bài báo Q1, kết hợp thực nghiệm Agentic với phân tích lý thuyết hình thức (Information Gain, Lipschitz Constant).

```bash
# Quy trình tự động: Suy luận -> Đo lường IG/Entropy -> Tự học Hebbian
python scripts/run_elite_pipeline.py --dataset hotpot_qa --limit 50
```

Kết quả sẽ được ghi nhận tại `reports/` với các chỉ số sâu về **Reasoning Density** và **Stability**.

---

## Bước 6: Phân tích lỗi sâu (RCA Decomposition)

Sau khi có kết quả, hãy phân loại lỗi theo chuẩn khoa học của chúng ta:

```bash
# Tự động phân tích lỗi dựa trên Elite Error Taxonomy (E-Ont, E-Trav, ...)
python scripts/run_rca_decomposition.py --input reports/temp_results.csv
```

---

## Bước 7: Phân tích Manifold & Trực quan hóa

Để có biểu đồ cho bài báo, hãy kích hoạt bộ phân tích cấu trúc:

```bash
# Tính toán hằng số Lipschitz và Silhouette Score cho Latent Ontology
python -m reasoning_ontology.src.manifold_analysis
```

---

## 8. Xem báo cáo tổng hợp

Hệ thống cung cấp một Control Panel giao diện web để theo dõi:

```bash
python -m control_panel.run
```
Truy cập: `http://localhost:8000`

---

## Phụ lục: Các file kết quả quan trọng
*   `reports/ig_reports.csv`: Mật độ lợi ích thông tin (IGpT).
*   `reports/manifold_stability.json`: Hằng số Lipschitz và độ bền bỉ.
*   `eval/data/*.csv`: Kết quả EM/F1 và Latency.
*   `docs/ACADEMIC_FORMALIZATION_Q1.md`: Tài liệu thuyết minh toán học.

---
**Chúc bạn có kết quả nghiên cứu đột phá!**
