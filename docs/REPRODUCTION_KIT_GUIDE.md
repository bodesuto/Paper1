# Reproduction Kit & Audit Guide (Q1 Standard)

Tài liệu này cung cấp hướng dẫn cho các Reviewer và Nhà nghiên cứu để tái thực hiện các thí nghiệm trong bài báo và xác minh các tuyên bố khoa học của DualMemoryKG.

---

## 1. Môi trường Thực nghiệm (Experiments Environment)
Để đảm bảo tính nhất quán (Consistency), chúng tôi đã đóng gói các phiên bản thư viện cụ thể trong file `pyproject.toml`.

*   **Python:** 3.10+
*   **Neo4j:** 5.x (Cơ sở dữ liệu biểu trưng)
*   **ChromaDB:** (Cơ sở dữ liệu vector)
*   **LLM:** Gemini-1.5-Pro / GPT-4o (Được cấu hình trong `common/models.py`)

---

## 2. Quy trình Tái thực nghiệm (Step-by-Step Reproduction)

### Bước 1: Khởi tạo Tri thức nền
Tái cấu trúc Đồ thị Tri thức từ các bộ dữ liệu thô:
```bash
python knowledge_graph/src/build_graph_v2.py --dataset hotpot_qa
```

### Bước 2: Chạy bộ thực nghiệm đối đầu (SOTA Benchmarking)
Kích hoạt Master Pipeline để so sánh với các Baseline:
```bash
python scripts/run_elite_pipeline.py --limit 100 --dataset hotpot_qa
```

### Bước 3: Xác minh các Định lý toán học (Mathematical Audit)
Các thuộc tính về **Lipschitz Stability** và **Entropy Decay** có thể được kiểm chứng qua log của diagnostics:
```bash
# Kiểm tra sự hội tụ Entropy
tail -f logs/entropy_tracker.log
```

---

## 3. Bản đồ dữ liệu (Data Provenance)
Tất cả kết quả thô phục vụ biểu đồ trong bài báo được lưu trữ tại:
*   `reports/figures/`: Ảnh biểu đồ PNG (300 DPI).
*   `reports/temp_results.csv`: Dữ liệu gốc cho các phép kiểm tra thống kê (T-test, P-value).

---

## 4. Cam kết về Tính Minh bạch (Transparency Statement)
Chúng tôi cam kết rằng không có sự "cherry-picking" trong kết quả. Mọi Case Study trong bài báo được trích xuất ngẫu nhiên thông qua module `CaseStudyExporter` từ các đợt chạy chính thức.

---
**DualMemoryKG Team** - *Towards Open and Reproducible AI Research.*
