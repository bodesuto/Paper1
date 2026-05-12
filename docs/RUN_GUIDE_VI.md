# HƯỚNG DẪN CHẠY HỆ THỐNG DUALMEMORYKG (STEP-BY-STEP)

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

## Bước 5: Chạy thí nghiệm Dual-Memory (Core Research)

Đây là phần quan trọng nhất để lấy dữ liệu cho bài báo Q1.

```bash
# Chạy ReAct với cơ chế Dual Memory (Knowledge Graph + Learned Ontology)
python scripts/run_ablation_suite.py --agent react --limit 5

# Chạy Reflexion (có cơ chế tự suy ngẫm)
python scripts/run_ablation_suite.py --agent reflexion --limit 5
```

*Lưu ý: Bạn có thể bỏ flag `--limit` để chạy toàn bộ dataset khi đã sẵn sàng.*

---

## Bước 6: Phân tích lỗi sâu (RCA Decomposition)

Sau khi có kết quả chạy ở Bước 5, hãy phân loại lỗi để viết phần "Discussion" cho bài báo:

```bash
# Tự động phân tích lỗi dựa trên Error Taxonomy (E-Ont, E-Trav, ...)
python scripts/run_rca_decomposition.py --input eval/data/react_full.csv
```

---

## Bước 7: Xem báo cáo tổng hợp

Hệ thống cung cấp một Control Panel giao diện web để bạn theo dõi:

```bash
# Khởi chạy giao diện quản lý
python -m control_panel.run
```
Sau đó truy cập: `http://localhost:8000` trên trình duyệt.

---

## Phụ lục: Các file kết quả quan trọng
*   `eval/data/*.csv`: Chứa điểm số (Exact Match, Latency, Tool Calls).
*   `output/*.rca.json`: Chứa kết quả phân tích nguyên nhân lỗi gốc.
*   `docs/`: Chứa các tài liệu học thuật liên quan.

---
**Chúc bạn có kết quả nghiên cứu tốt!**
