# Xử Lý Sự Cố

Tài liệu này gom các lỗi bạn rất dễ gặp khi chạy repo và cách sửa ngắn nhất.

Nếu bạn chưa đọc hướng dẫn chạy chính, xem trước [REPRODUCTION_GUIDE_VI.md](./REPRODUCTION_GUIDE_VI.md).

---

## 1. `ModuleNotFoundError`

### Ví dụ

- `ModuleNotFoundError: No module named 'langchain.callbacks'`
- `ModuleNotFoundError: No module named 'langchain.schema'`
- `ModuleNotFoundError: No module named 'langchain_google_genai'`
- `ModuleNotFoundError: No module named 'neo4j'`
- `ModuleNotFoundError: No module named 'pandas'`

### Nguyên nhân thường gặp

- chưa activate đúng môi trường
- chưa cài đủ package trong `requirements.txt`
- đang chạy bằng Python của hệ thống thay vì env `researchpaper` hoặc `.venv`

### Cách xử lý

Kiểm tra Python đang dùng:

```powershell
python -c "import sys; print(sys.executable)"
```

Cài lại package:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

Nếu dùng Conda:

```powershell
conda activate researchpaper
pip install -r requirements.txt
```

---

## 2. `ValueError: Missing required env var`

### Ví dụ

- `Missing required env var: GOOGLE_API_KEY`
- `Missing required env var: CONFIDENT_API_KEY`

### Nguyên nhân

Thiếu biến trong `.env`.

### Cách xử lý

Mở `.env` và thêm biến thiếu.

Lưu ý:

- `GOOGLE_API_KEY` là bắt buộc cho Gemini runtime
- `CONFIDENT_API_KEY` hiện không còn là blocker cho mọi path, nhưng một số flow cũ hoặc tooling ngoài có thể vẫn cần

---

## 3. Cảnh báo `Both GOOGLE_API_KEY and GEMINI_API_KEY are set`

### Triệu chứng

Bạn thấy log kiểu:

- `Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.`

### Ý nghĩa

Code hiện tại trong [env_setup.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/common/env_setup.py) sẽ set `GEMINI_API_KEY` alias từ `GOOGLE_API_KEY` để tương thích với một số SDK.

Nếu bạn vừa khai báo `GOOGLE_API_KEY` trong `.env`, vừa có `GEMINI_API_KEY` ở môi trường hệ thống, bạn sẽ thấy cảnh báo này.

### Cách xử lý

Giữ một nguồn duy nhất:

- cách đơn giản nhất là chỉ giữ `GOOGLE_API_KEY`
- bỏ `GEMINI_API_KEY` khỏi shell hoặc biến hệ thống nếu không cần

---

## 4. Gemini `404 NOT_FOUND`

### Ví dụ

- `Error calling model 'gemini-1.5-flash' (NOT_FOUND)`
- `models/... is not found for API version v1beta`

### Nguyên nhân

- tên model sai
- model đó không còn được hỗ trợ trên method đang gọi

### Cách xử lý

Dùng model ổn định hơn trong `.env`:

```env
GEMINI_MODEL_NAME=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001
```

Sau đó test lại:

```powershell
python .\scripts\run_test_llm.py
```

---

## 5. Gemini `429 RESOURCE_EXHAUSTED`

### Ví dụ

- `Quota exceeded`
- `Please retry in ... seconds`

### Nguyên nhân

- free tier bị giới hạn request/phút
- chạy DeepEval + agent + stress/ablation cùng lúc làm quota tăng rất nhanh

### Cách xử lý

- chờ hết cửa sổ rate limit
- chạy mini data trước
- giảm `--limit` hoặc `--row-limit`
- không chạy nhiều script nặng đồng thời
- nếu cần, nâng billing plan

Các script rẻ nhất để debug trước:

```powershell
python .\scripts\run_test_llm.py
python .\scripts\run_prepare_mini_data.py --size 3
python .\scripts\run_react_smoke.py --limit 1
```

---

## 6. Neo4j connection lỗi

### Ví dụ

- `Failed to establish connection`
- `Unauthorized`
- graph-based scripts bị crash khi gọi `GraphDatabase.driver(...)`

### Nguyên nhân

- `NEO4J_URI` sai
- `NEO4J_USER` / `NEO4J_PASSWORD` sai
- Neo4j chưa chạy
- database name sai

### Cách xử lý

Kiểm tra `.env`:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
```

Sau đó chạy lại bước insert:

```powershell
python .\scripts\run_insert_obs.py
```

---

## 7. Lỗi vector index / embedding dimension

### Triệu chứng

- insert graph bị lỗi khi tạo vector index
- Neo4j báo vector dimension mismatch

### Nguyên nhân

Gemini embedding dimension không khớp với index được tạo cứng trước đó.

### Cách xử lý

Code hiện tại đã hỗ trợ 2 cách:

1. để trống `EMBEDDING_VECTOR_DIMENSIONS` để runtime tự probe
2. tự set đúng dimension trong `.env`

Ví dụ:

```env
EMBEDDING_VECTOR_DIMENSIONS=
```

Nếu bạn đã có index cũ sai dimension, cần xóa/rebuild schema của Neo4j trước khi insert lại.

---

## 8. `full` mode không chạy hoặc chạy nhưng không khác `learned`

### Triệu chứng

- `FileNotFoundError` cho traversal policy checkpoint
- `full` cho kết quả giống `learned`

### Nguyên nhân

Bạn chưa build traversal policy checkpoint.

### Cách xử lý

Chạy đúng thứ tự:

```powershell
python .\scripts\run_build_ontology_dataset.py
python .\scripts\run_fit_ontology_prototypes.py
python .\scripts\run_react_learned.py
python .\scripts\run_build_policy_dataset.py --input-path .\eval\data\react_learned.csv
python .\scripts\run_fit_traversal_policy.py
python .\scripts\run_react_full.py
```

---

## 9. HIL chưa xong nên pipeline bị chặn

### Triệu chứng

- `run_classify.py` không ra file
- thiếu `.hil.json`

### Nguyên nhân

Pipeline gốc cần human review hoàn tất trước khi classify.

### Cách xử lý

Chạy:

```powershell
python .\scripts\run_hil_streamlit.py
```

Hoàn thành review xong mới chuyển sang:

```powershell
python .\scripts\run_classify.py
```

---

## 10. `Import-Csv` không chạy trong terminal

### Triệu chứng

Bạn gõ:

```powershell
Import-Csv ...
```

nhưng terminal báo:

- `'Import-Csv' is not recognized as an internal or external command`

### Nguyên nhân

Bạn đang ở `cmd` shell chứ không phải PowerShell thật.

### Cách xử lý

Hoặc chuyển terminal sang PowerShell, hoặc dùng Python thay thế:

```powershell
python -c "import pandas as pd; pd.read_csv(r'.\eval\data\hard_bridge_500_train.csv').head(3).to_csv(r'.\eval\data\mini_train_3.csv', index=False)"
```

Repo hiện đã có script tiện hơn:

```powershell
python .\scripts\run_prepare_mini_data.py --size 3
```

---

## 11. DeepEval/Gemini metric lỗi nhưng eval không dừng

### Triệu chứng

- một số metric trả về `metric_error: ...`
- CSV vẫn được sinh ra

### Ý nghĩa

Code hiện tại trong [matrics.py](F:/Luận%20văn%20thạc%20sĩ/Paper/purpose/Paper1/DualMemoryKG/eval/test/matrics.py) dùng `safe_measure()` để không làm gãy toàn bộ evaluation khi model evaluator bị lỗi.

### Cách xử lý

- nếu chỉ smoke run, có thể chấp nhận
- nếu làm paper run, cần rerun sau khi quota/model ổn định hơn

---

## 12. Một bước chạy xong nhưng không thấy file output

Đi theo bảng sau:

- thiếu `.json` export:
  - kiểm tra `run_export.py`
- thiếu `.react.txt`:
  - kiểm tra `run_format_trace.py`
- thiếu `.rca.json`:
  - kiểm tra `run_rca.py`
- thiếu `.kbv.json`:
  - kiểm tra `run_kbv.py`
- thiếu `.hil.json`:
  - HIL chưa hoàn tất
- thiếu `.classified.json`:
  - `run_classify.py` chưa chạy đúng
- thiếu `.ontology_prototypes.json`:
  - chưa build ontology dataset hoặc fit ontology
- thiếu `.traversal_policy.json`:
  - chưa build policy dataset hoặc chưa fit traversal
- thiếu `react_full.csv`:
  - graph chưa sẵn sàng hoặc thiếu traversal checkpoint

---

## 13. Cách debug ngắn nhất theo thứ tự

Nếu repo đang lỗi và bạn muốn debug nhanh nhất:

```powershell
python .\scripts\run_test_llm.py
python .\scripts\run_prepare_mini_data.py --size 3
python .\scripts\run_react_smoke.py --limit 1
python .\scripts\run_reflexion_smoke.py --limit 1
python .\scripts\run_build_ontology_dataset.py
python .\scripts\run_fit_ontology_prototypes.py
python .\scripts\run_react_learned.py
python .\scripts\run_build_policy_dataset.py --input-path .\eval\data\react_learned.csv
python .\scripts\run_fit_traversal_policy.py
```

Khi chuỗi này ổn rồi mới chuyển sang full pipeline gốc và ablation suite.
