# DualMemoryKG: Full-Scale Experiment Execution Guide (10,000 Queries)

Tài liệu này hướng dẫn bạn thực hiện quy trình thực nghiệm toàn diện từ A-Z để phục vụ bài báo Q1. Quy trình này đã được tích hợp các cơ chế bảo vệ tài chính (Cost-Control), chống mất dữ liệu (Atomic Resume), và phân tích SOTA tự động.

---

## 🛠 Bước 1: Chuẩn bị Môi trường (Pre-flight Check)
Trước khi bắt đầu bất kỳ đợt chạy nào kéo dài hàng chục giờ, bạn **PHẢI** kiểm tra tính sẵn sàng của hạ tầng.

1.  **Cập nhật môi trường:** Đảm bảo `.env` đã có `GEMINI_API_KEY`, `NEO4J_URI`, `NEO4J_PASSWORD`.
2.  **Chạy script kiểm tra:**
    ```bash
    python scripts/pre_flight_check.py
    ```
    *Script này sẽ kiểm tra: Kết nối Neo4j, Gemini API Quota, ChromaDB, và logic Information-Theoretic (IT).*

---

## 🔬 Bước 2: Chạy Thăm dò & Ước tính Chi phí (Probe Phase)
Đừng chạy 10,000 câu ngay lập tức. Hãy chạy thăm dò 100 câu để xem hiệu năng và chi phí dự kiến.

```bash
python scripts/run_controlled_full.py --strategy heuristic --probe
```

**Kết quả sau bước này:**
- Kiểm tra file `eval/data/ablations/react_heuristic_probe100.csv`.
- Xem báo cáo trên Terminal: **"Projected 10k cost: $X.XX"**. Nếu số tiền vượt quá ngân sách, bạn nên giảm bộ dữ liệu hoặc đổi model.

---

## 🚀 Bước 3: Chạy Thực nghiệm Chính thức (Execution Phase)
Khi đã hài lòng với chi phí thăm dò, hãy chạy full bộ dữ liệu. Chúng tôi khuyến nghị chạy từng chiến lược một để dễ kiểm soát.

### 1. Chạy Baseline (So sánh chuẩn)
```bash
python scripts/run_controlled_full.py --strategy vector_rag
```

### 2. Chạy DualMemoryKG (Heuristic - Q1 Focus)
```bash
python scripts/run_controlled_full.py --strategy heuristic
```

### 3. Chạy các biến thể khác (Ablation Study)
```bash
python scripts/run_controlled_full.py --strategy graph_rag
python scripts/run_controlled_full.py --strategy ontology_only
```

> **Lưu ý:** Nếu giữa chừng bị mất mạng hoặc sập nguồn, bạn chỉ cần gõ lại lệnh cũ. Hệ thống sẽ tự động **RESUME** từ câu hỏi cuối cùng chưa hoàn thành.

---

## 📊 Bước 4: Khai thác & Phân tích SOTA (Mining & Analysis)
Sau khi đã có các file kết quả `.csv` trong thư mục `eval/data/ablations/`, hãy chạy pipeline phân tích tự động để tạo nội dung cho bài báo.

```bash
python scripts/run_analysis_pipeline.py
```

**Các tệp tin sẽ được sinh ra tại thư mục `reports/`:**
1.  **`sota_comparison_table.csv`**: Bảng so sánh trực tiếp với Self-RAG và GraphRAG.
2.  **`figures/sota_radar.png`**: Biểu đồ Radar đa góc độ (Accuracy, Faithfulness, Efficiency).
3.  **`figures/ablation_heatmap.png`**: Heatmap chứng minh tác động của từng thành phần bộ nhớ.
4.  **`bootstrap_ci_table.csv`**: Bảng ý nghĩa thống kê (Statistical Significance) với khoảng tin cậy 95%.

---

## 📉 Bước 5: Báo cáo Khoa học (Final Synthesis)
Để có bảng tổng hợp cuối cùng cho bản thảo bài báo:

```bash
python scripts/run_result_summary.py --inputs eval/data/ablations/*.csv --reference eval/data/ablations/react_baseline.csv --output-path reports/final_master_summary.csv
```

---

## ⚠️ Các quy tắc an toàn (Golden Rules)
1.  **RPM Limit:** Hệ thống được cấu hình mặc định 12 RPM để tránh bị Gemini khóa API. Không nên tăng số này trừ khi bạn có tài khoản Enterprise.
2.  **Budget Stop:** Mồi chiến lược được giới hạn tự động dừng ở **$8.0**. Bạn có thể điều chỉnh con số này trong `react_test.py`.
3.  **Neo4j Monitoring:** Đảm bảo Neo4j không bị tràn bộ nhớ. Nên restart Neo4j Container sau mỗi 2 chiến lược lớn.
