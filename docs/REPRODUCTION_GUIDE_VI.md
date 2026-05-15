# Huong Dan Tai Hien Repo Chi Tiet

> [!IMPORTANT]
> Đối với quy trình thực nghiệm hiệu năng cao (10,000 câu hỏi) cho bài báo Q1, hãy sử dụng hướng dẫn mới nhất tại đây: [**EXPERIMENT_GUIDE_V2.md**](../EXPERIMENT_GUIDE_V2.md)

Tai lieu nay bam theo code hien tai cua repo sau migration sang Langfuse.

No bao gom:

1. cai moi truong
2. chay mini de thong luong
3. bat Neo4j va Langfuse local
4. export trace -> format -> RCA -> KBV -> HIL -> classify -> insert graph
5. build ontology + traversal artifacts
6. chay baseline, ablation, stress, transfer, summary

## 1. Yeu cau moi truong

- Python 3.10+
- mot env da cai `requirements.txt`
- Gemini API key
- Neo4j co ho tro vector index
- Langfuse chi can khi ban muon observability/tracing/export

Neu dung Conda:

```powershell
conda activate researchpaper
pip install -r requirements.txt
```

Neu dung venv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## 2. `.env` can chinh

```env
GOOGLE_API_KEY=your_google_api_key
GEMINI_MODEL_NAME=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001

LANGFUSE_TRACING_ENABLED=false
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_ENVIRONMENT=local
LANGFUSE_RELEASE=
LANGFUSE_TRACE_NAME=
OUTPUT_PATH=./output/langfuse_export.json
DATA_PATH=./eval/data

CONFIDENT_API_KEY=

RETRIEVAL_STRATEGY=heuristic
ONTOLOGY_PROTOTYPES_PATH=./output/langfuse_export.ontology_prototypes.json
ONTOLOGY_TOP_K=5
LEARNED_RETRIEVAL_TOP_K=6
TRAVERSAL_POLICY_PATH=./output/langfuse_export.traversal_policy.json
TRAVERSAL_TOP_K=3

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j

EMBEDDING_VECTOR_DIMENSIONS=
```

Luu y:

- giu mot trong hai bien `GOOGLE_API_KEY` hoac `GEMINI_API_KEY`
- `CONFIDENT_API_KEY` la optional, khong bat buoc de chay local

## 3. Kiem tra moi truong

```powershell
python .\scripts\run_test_llm.py
```

Neu loi:

- `ModuleNotFoundError`: cai lai package
- `Missing required env var`: thieu bien trong `.env`
- `404 NOT_FOUND`: sai ten model Gemini
- `429 RESOURCE_EXHAUSTED`: het quota

## 4. Chay mini de thong luong

```powershell
python .\scripts\run_prepare_mini_data.py --size 3
python .\scripts\run_react_smoke.py --limit 1
python .\scripts\run_reflexion_smoke.py --limit 1
```

Artifacts:

- `.\eval\data\mini_train_3.csv`
- `.\eval\data\mini_validation_3.csv`
- `.\eval\data\react_smoke_results.csv`
- `.\eval\data\reflexion_smoke_results.csv`

## 5. Bat dich vu local

### 5.1. Neo4j

```powershell
docker compose up -d
docker compose ps
```

Default local config:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=dualmemorykg123
NEO4J_DATABASE=neo4j
```

### 5.2. Langfuse

```powershell
docker compose --profile langfuse up -d
docker compose --profile langfuse ps
```

Set:

```env
LANGFUSE_TRACING_ENABLED=true
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_PUBLIC_KEY=pk-lf-local-public-key
LANGFUSE_SECRET_KEY=sk-lf-local-secret-key
```

UI:

- `http://localhost:3000`

## 6. Tai hien pipeline observability goc, nhung bang Langfuse

### Buoc 6.1. Tao trace

Chay mot vai smoke hoac experiment script khi `LANGFUSE_TRACING_ENABLED=true`.

### Buoc 6.2. Export trace

```powershell
python .\scripts\run_export.py
```

Expected:

- `.\output\langfuse_export.json`

### Buoc 6.3. Format ReAct trace

```powershell
python .\scripts\run_format_trace.py
```

Expected:

- `.\output\langfuse_export.react.txt`

### Buoc 6.4. RCA

```powershell
python .\scripts\run_rca.py
```

Expected:

- `.\output\langfuse_export.rca.json`

### Buoc 6.5. KBV

```powershell
python .\scripts\run_kbv.py
```

Expected:

- `.\output\langfuse_export.kbv.json`

### Buoc 6.6. Human review

```powershell
python .\scripts\run_hil_streamlit.py
```

Expected:

- `.\output\langfuse_export.hil.json`

### Buoc 6.7. Classify

```powershell
python .\scripts\run_classify.py
```

Expected:

- `.\output\langfuse_export.classified.json`
- `.\output\langfuse_export.classified_insights.json`

### Buoc 6.8. Insert vao Neo4j

```powershell
python .\scripts\run_insert_obs.py
```

## 7. Build ontology va traversal

```powershell
python .\scripts\run_build_ontology_dataset.py
python .\scripts\run_fit_ontology_prototypes.py
python .\scripts\run_insert_obs.py
python .\scripts\run_react_learned.py
python .\scripts\run_build_policy_dataset.py --input-path .\eval\data\react_learned.csv
python .\scripts\run_fit_traversal_policy.py
```

Expected:

- `.\output\langfuse_export.ontology_dataset.json`
- `.\output\langfuse_export.ontology_prototypes.json`
- `.\output\langfuse_export.traversal_policy_dataset.json`
- `.\output\langfuse_export.traversal_policy.json`

## 8. Chay baseline va full mode

ReAct:

```powershell
python .\scripts\run_react_baseline.py
python .\scripts\run_react_heuristic.py
python .\scripts\run_react_vector_rag.py
python .\scripts\run_react_graph_rag.py
python .\scripts\run_react_ontology_only.py
python .\scripts\run_react_traversal_only.py
python .\scripts\run_react_learned.py
python .\scripts\run_react_full.py
```

Reflexion:

```powershell
python .\scripts\run_reflexion_baseline.py
python .\scripts\run_reflexion_heuristic.py
python .\scripts\run_reflexion_vector_rag.py
python .\scripts\run_reflexion_graph_rag.py
python .\scripts\run_reflexion_ontology_only.py
python .\scripts\run_reflexion_traversal_only.py
python .\scripts\run_reflexion_learned.py
python .\scripts\run_reflexion_full.py
```

## 9. Chay paper-level suites

```powershell
python .\scripts\run_ablation_suite.py --agent react
python .\scripts\run_ablation_suite.py --agent reflexion
python .\scripts\run_stress_suite.py --agent react --strategy full --stress noisy --output-path .\eval\data\react_stress_noisy.csv
python .\scripts\run_transfer_eval.py --in-domain .\eval\data\ablations\react_full.csv --out-of-domain .\eval\data\reflexion_full.csv --output-path .\eval\data\transfer_summary.csv
python .\scripts\run_result_summary.py --inputs .\eval\data\ablations\react_baseline.csv .\eval\data\ablations\react_full.csv .\eval\data\ablations\reflexion_baseline.csv .\eval\data\ablations\reflexion_full.csv --output-path .\eval\data\paper_summary.csv
```

## 10. Neu muon thao tac bang UI

```powershell
python .\scripts\run_control_panel.py
```

Mo `http://127.0.0.1:8787`.

Control panel da duoc cap nhat de hien thi cau hinh Langfuse thay cho tracing backend cu.
