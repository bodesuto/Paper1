# Huong Dan Chay Tiep Tu Moc Hien Tai

Tai lieu nay bat dau tu trang thai ban da xac nhan chay duoc:

```powershell
cd "F:\Luận văn thạc sĩ\Paper\purpose\Paper1\DualMemoryKG"
conda activate researchpaper
pip install -r requirements.txt
python .\scripts\run_test_llm.py
python .\scripts\run_prepare_mini_data.py --size 3
python .\scripts\run_react_smoke.py --limit 1
python .\scripts\run_reflexion_smoke.py --limit 1
```

Dieu nay co nghia la:

- moi truong Python da on
- Gemini goi duoc
- mini dataset da co
- ReAct va Reflexion da smoke-test thanh cong

## 1. Ban dang o dau

Sau cac buoc tren, repo cua ban da qua pha "LLM + agent sanity check".

Buoc tiep theo dung la:

1. neu muon kiem nghiem re va nhanh: chay pipeline mini dual-memory
2. neu muon tai hien day du pipeline observability: bat Langfuse va export trace
3. sau khi graph/prototype/policy on dinh: chay full ablation va summary

## 2. `.env` toi thieu can co

```env
GOOGLE_API_KEY=
GEMINI_MODEL_NAME=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001

LANGFUSE_TRACING_ENABLED=false
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
OUTPUT_PATH=./output/langfuse_export.json
DATA_PATH=./eval/data

CONFIDENT_API_KEY=

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j

RETRIEVAL_STRATEGY=heuristic
ONTOLOGY_PROTOTYPES_PATH=./output/langfuse_export.ontology_prototypes.json
TRAVERSAL_POLICY_PATH=./output/langfuse_export.traversal_policy.json
```

Luu y:

- giu mot trong hai bien `GOOGLE_API_KEY` hoac `GEMINI_API_KEY`
- `CONFIDENT_API_KEY` khong bat buoc neu ban chi muon chay local metric
- `LANGFUSE_*` chi bat buoc khi ban muon trace/export observability

## 3. Docker cac dich vu local

### 3.1. Neo4j

```powershell
docker compose up -d
docker compose ps
```

Mac dinh:

- Neo4j Browser: `http://localhost:7474`
- Bolt: `bolt://localhost:7687`
- user: `neo4j`
- password: `dualmemorykg123`

Neu `.env` dang tro vao Aura, doi lai:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=dualmemorykg123
NEO4J_DATABASE=neo4j
```

### 3.2. Langfuse self-host

```powershell
docker compose --profile langfuse up -d
docker compose --profile langfuse ps
```

Cac endpoint local:

- Langfuse UI: `http://localhost:3000`
- MinIO API: `http://localhost:9000`
- MinIO Console: `http://localhost:9001`
- ClickHouse HTTP: `http://localhost:8123`

Trong `.env`, set:

```env
LANGFUSE_TRACING_ENABLED=true
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_PUBLIC_KEY=pk-lf-local-public-key
LANGFUSE_SECRET_KEY=sk-lf-local-secret-key
```

## 4. Lo trinh mini de kiem nghiem thong luong

Ban da chay xong 4 lenh dau. Tiep theo chay theo thu tu:

### Step 4.1. ReAct baseline mini

```powershell
python .\scripts\run_experiment.py --agent react --mode baseline --strategy heuristic --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_baseline_mini.csv
```

### Step 4.2. ReAct dual-memory heuristic mini

```powershell
python .\scripts\run_experiment.py --agent react --mode dual_memory --strategy heuristic --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_heuristic_mini.csv
```

### Step 4.3. ReAct vector-rag mini

```powershell
python .\scripts\run_experiment.py --agent react --mode dual_memory --strategy vector_rag --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_vector_rag_mini.csv
```

### Step 4.4. ReAct graph-rag mini

```powershell
python .\scripts\run_experiment.py --agent react --mode dual_memory --strategy graph_rag --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_graph_rag_mini.csv
```

Neu muon them Reflexion mini:

```powershell
python .\scripts\run_experiment.py --agent reflexion --mode baseline --strategy heuristic --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\reflexion_baseline_mini.csv
python .\scripts\run_experiment.py --agent reflexion --mode dual_memory --strategy heuristic --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\reflexion_heuristic_mini.csv
```

## 5. Lo trinh observability -> graph bang Langfuse

Phan nay dung khi ban muon tai hien luong export/trace/graph day du.

### Step 5.1. Bat tracing

Trong `.env`:

```env
LANGFUSE_TRACING_ENABLED=true
```

### Step 5.2. Tao trace bang smoke hoac experiment

Vi du:

```powershell
python .\scripts\run_react_smoke.py --limit 1
python .\scripts\run_reflexion_smoke.py --limit 1
```

### Step 5.3. Export trace tu Langfuse

```powershell
python .\scripts\run_export.py
```

Ky vong:

- `.\output\langfuse_export.json`

### Step 5.4. Format trace

```powershell
python .\scripts\run_format_trace.py
```

Ky vong:

- `.\output\langfuse_export.react.txt`

### Step 5.5. RCA + KBV + HIL + classify + insert

```powershell
python .\scripts\run_rca.py
python .\scripts\run_kbv.py
python .\scripts\run_hil_streamlit.py
python .\scripts\run_classify.py
python .\scripts\run_insert_obs.py
```

## 6. Build ontology va traversal artifacts

Sau khi da co classified artifacts va graph:

```powershell
python .\scripts\run_build_ontology_dataset.py
python .\scripts\run_fit_ontology_prototypes.py
python .\scripts\run_insert_obs.py
python .\scripts\run_react_learned.py
python .\scripts\run_build_policy_dataset.py --input-path .\eval\data\react_learned.csv
python .\scripts\run_fit_traversal_policy.py
```

Ky vong:

- `.\output\langfuse_export.ontology_dataset.json`
- `.\output\langfuse_export.ontology_prototypes.json`
- `.\output\langfuse_export.traversal_policy_dataset.json`
- `.\output\langfuse_export.traversal_policy.json`

## 7. Chay full baseline/ablation sau khi bootstrap xong

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

## 8. Neu ban muon giao dien web thay vi CLI

```powershell
python .\scripts\run_control_panel.py
```

Mo:

```text
http://127.0.0.1:8787
```

Control panel da duoc doi sang Langfuse-first cho phan env va export trace.

## 9. Ket luan thuc dung

Tu moc hien tai cua ban, thu tu hop ly nhat la:

1. chay het mini experiment
2. bat Neo4j local
3. bat Langfuse neu muon luu/export trace
4. export -> format -> RCA -> KBV -> HIL -> classify -> insert
5. build ontology + traversal
6. chay ablation/full summary

Neu ban muon, buoc tiep theo toi co the viet them:

- mot `RUN_MINI_GRAPH.md` rieng chi gom lenh mini
- mot `RUN_FULL_PAPER.md` rieng chi gom lenh full
- hoac patch them control panel de co nut "Start Langfuse stack" va "Open Langfuse UI"

Neu ban muon mot tai lieu chi gom tung step mot cho du lieu nho, xem:

- [RUN_MINI_FIRST_VI.md](./RUN_MINI_FIRST_VI.md)
