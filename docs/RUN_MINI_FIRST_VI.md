# Huong Dan Chay Tung Step Mot Tren Du Lieu Nho

> [!IMPORTANT]
> Nếu mục tiêu của bạn là chạy thực nghiệm Full-Scale (10,000 câu hỏi) cho bài báo Q1, hãy sử dụng quy trình đã được tối ưu hóa tại đây: [**EXPERIMENT_GUIDE_V2.md**](../EXPERIMENT_GUIDE_V2.md)

Tai lieu nay danh cho muc tieu:

- chay repo thong luong truoc
- dung tap mini de tiet kiem quota va thoi gian
- moi buoc deu co checkpoint ro rang
- sau khi mini on moi mo rong sang full

Tai lieu nay uu tien:

1. de chay
2. it loi
3. de debug

## 0. Muc tieu cua lo trinh nay

Ban se di theo 4 pha:

1. xac minh moi truong
2. chay mini baseline va mini dual-memory
3. chay mini graph + ontology + traversal
4. mo rong sang ablation, annotation, figure va full run

Neu dang bi loi o pha nao, dung lai o pha do, khong nhay qua pha sau.

## 1. Chuan bi moi truong

Mo terminal VSCode va chay:

```powershell
cd "F:\Luận văn thạc sĩ\Paper\purpose\Paper1\DualMemoryKG"
conda activate researchpaper
pip install -r requirements.txt
```

### 1.1. Kiem tra `.env`

Toi thieu nen co:

```env
GOOGLE_API_KEY=your_google_api_key
GEMINI_MODEL_NAME=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=dualmemorykg123
NEO4J_DATABASE=neo4j

LANGFUSE_TRACING_ENABLED=false
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=

ALLOW_DEFAULT_EXAMPLE_PADDING=false
OUTPUT_PATH=./output/langfuse_export.json
DATA_PATH=./eval/data
```

### 1.2. Checkpoint

Neu ban chua sua `.env`, dung lai va sua truoc.

## 2. Pha A: Kiem tra moi truong va mini smoke

### Step A1. Test LLM

```powershell
python .\scripts\run_test_llm.py
```

### Ky vong

- model tra ve 1 cau ngan
- khong co `ModuleNotFoundError`
- khong co `Missing required env var`

### Neu loi

- `404`: sai ten model
- `429`: het quota
- `API key expired`: doi key

Chi khi Step A1 pass moi sang A2.

### Step A2. Tao mini data

```powershell
python .\scripts\run_prepare_mini_data.py --size 3
```

### Ky vong

Tao ra:

- `.\eval\data\mini_train_3.csv`
- `.\eval\data\mini_validation_3.csv`

### Step A3. Chay ReAct smoke

```powershell
python .\scripts\run_react_smoke.py --limit 1
```

### Step A4. Chay Reflexion smoke

```powershell
python .\scripts\run_reflexion_smoke.py --limit 1
```

### Checkpoint ket thuc Pha A

Neu 4 lenh duoi day deu chay duoc:

```powershell
python .\scripts\run_test_llm.py
python .\scripts\run_prepare_mini_data.py --size 3
python .\scripts\run_react_smoke.py --limit 1
python .\scripts\run_reflexion_smoke.py --limit 1
```

thi repo da thong duoc:

- env
- Gemini
- import
- ReAct
- Reflexion

Luc nay moi sang Pha B.

## 3. Pha B: Chay mini baseline va mini dual-memory

### Step B1. Bat Neo4j local

```powershell
docker compose up -d
docker compose ps
```

### Ky vong

- container `neo4j` dang chay
- co the mo `http://localhost:7474`

### Step B2. ReAct baseline mini

```powershell
python .\scripts\run_experiment.py --agent react --mode baseline --strategy heuristic --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_baseline_mini.csv
```

### Step B3. ReAct heuristic mini

```powershell
python .\scripts\run_experiment.py --agent react --mode dual_memory --strategy heuristic --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_heuristic_mini.csv
```

### Step B4. ReAct vector-rag mini

```powershell
python .\scripts\run_experiment.py --agent react --mode dual_memory --strategy vector_rag --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_vector_rag_mini.csv
```

### Step B5. ReAct graph-rag mini

```powershell
python .\scripts\run_experiment.py --agent react --mode dual_memory --strategy graph_rag --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_graph_rag_mini.csv
```

### Step B6. Neu muon, chay Reflexion mini

```powershell
python .\scripts\run_experiment.py --agent reflexion --mode baseline --strategy heuristic --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\reflexion_baseline_mini.csv
python .\scripts\run_experiment.py --agent reflexion --mode dual_memory --strategy heuristic --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\reflexion_heuristic_mini.csv
```

### Checkpoint ket thuc Pha B

Neu ban da co cac file:

- `react_baseline_mini.csv`
- `react_heuristic_mini.csv`
- `react_vector_rag_mini.csv`
- `react_graph_rag_mini.csv`

thi co nghia la:

- baseline da chay
- retrieval modes da chay
- Neo4j da noi duoc

Luc nay moi sang Pha C.

## 4. Pha C: Chay mini graph + ontology + traversal

Pha nay la pha quan trong nhat neu muc tieu cua ban la sau nay chay paper-grade pipeline.

### Step C1. Bat Langfuse local

```powershell
docker compose --profile langfuse up -d
docker compose --profile langfuse ps
```

Trong `.env`, sua:

```env
LANGFUSE_TRACING_ENABLED=true
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_PUBLIC_KEY=pk-lf-local-public-key
LANGFUSE_SECRET_KEY=sk-lf-local-secret-key
```

### Step C2. Tao trace nho

```powershell
python .\scripts\run_react_smoke.py --limit 1
python .\scripts\run_reflexion_smoke.py --limit 1
```

### Step C3. Export trace

```powershell
python .\scripts\run_export.py
```

### Step C4. Format trace

```powershell
python .\scripts\run_format_trace.py
```

### Step C5. RCA

```powershell
python .\scripts\run_rca.py
```

### Step C6. KBV

```powershell
python .\scripts\run_kbv.py
```

### Step C7. HIL

```powershell
python .\scripts\run_hil_streamlit.py
```

Sau khi review xong tren UI, quay lai terminal.

### Step C8. Classify

```powershell
python .\scripts\run_classify.py
```

### Step C9. Insert graph

```powershell
python .\scripts\run_insert_obs.py
```

### Step C10. Build ontology dataset

```powershell
python .\scripts\run_build_ontology_dataset.py
```

### Step C11. Fit ontology prototypes tren train split

```powershell
python .\scripts\run_fit_ontology_prototypes.py --split train
```

### Step C12. Insert lai de enrich graph

```powershell
python .\scripts\run_insert_obs.py
```

### Step C13. Chay learned mini de tao retrieval logs

```powershell
python .\scripts\run_experiment.py --agent react --mode dual_memory --strategy learned --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_learned_mini.csv
```

### Step C14. Build traversal policy dataset

```powershell
python .\scripts\run_build_policy_dataset.py --input-path .\eval\data\react_learned_mini.csv
```

### Step C15. Fit traversal policy

```powershell
python .\scripts\run_fit_traversal_policy.py
```

### Step C16. Test full mini

```powershell
python .\scripts\run_experiment.py --agent react --mode dual_memory --strategy full --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_full_mini.csv
```

### Checkpoint ket thuc Pha C

Neu ban da co:

- `.\output\langfuse_export.json`
- `.\output\langfuse_export.ontology_dataset.train.json`
- `.\output\langfuse_export.ontology_prototypes.json`
- `.\output\langfuse_export.traversal_policy_dataset.train.json`
- `.\output\langfuse_export.traversal_policy.json`
- `.\eval\data\react_full_mini.csv`

thi mini graph pipeline da thong.

Luc nay ban moi nen sang Pha D.

## 5. Pha D: Mini paper-facing evaluation

Pha nay dung de kiem nghiem nhanh luong annotation, summary, figure.

### Step D1. Chay ablation suite tren mini hoac validation nho

Neu muon nhanh, ban co the chay rieng tung file CSV mini o Pha B va C.

Neu muon batch:

```powershell
python .\scripts\run_ablation_suite.py --agent react --data-path .\eval\data\mini_validation_3.csv --output-dir .\eval\data\ablations_mini
```

### Step D2. Tao summary

```powershell
python .\scripts\run_result_summary.py --inputs .\eval\data\ablations_mini\react_baseline.csv .\eval\data\ablations_mini\react_heuristic.csv .\eval\data\ablations_mini\react_vector_rag.csv .\eval\data\ablations_mini\react_graph_rag.csv .\eval\data\ablations_mini\react_ontology_only.csv .\eval\data\ablations_mini\react_traversal_only.csv .\eval\data\ablations_mini\react_learned.csv .\eval\data\ablations_mini\react_full.csv --reference .\eval\data\ablations_mini\react_baseline.csv --output-path .\eval\data\react_summary_mini.csv
```

### Step D3. Tao template annotation evidence

```powershell
python .\scripts\run_prepare_evidence_annotation.py --results-csv .\eval\data\ablations_mini\react_full.csv --output-path .\experiments\react_full_annotations_mini.json --limit 3
```

Mo file JSON vua tao va dien:

- `gold_evidence_node_ids`
- `sufficient_evidence_sets`
- `contradiction_node_ids`
- doi `annotation_status` thanh `done`

### Step D4. Chay annotated evidence eval

```powershell
python .\scripts\run_annotated_evidence_eval.py --results-csv .\eval\data\ablations_mini\react_full.csv --annotations-path .\experiments\react_full_annotations_mini.json --output-path .\experiments\react_full_evidence_eval_mini.csv --summary-path .\experiments\react_full_evidence_eval_mini_summary.json
```

### Step D5. Sinh figure

```powershell
python .\scripts\run_paper_figures.py --summary-csv .\eval\data\react_summary_mini.csv --results-csv .\eval\data\ablations_mini\react_full.csv --output-dir .\experiments\figures_mini
```

### Checkpoint ket thuc Pha D

Neu tao duoc:

- `react_summary_mini.csv`
- `react_full_annotations_mini.json`
- `react_full_evidence_eval_mini.csv`
- `fig_main_metrics.png`
- `fig_grounding_latency_tradeoff.png`
- `fig_ablation_heatmap.png`

thi luong paper-facing mini da thong.

## 6. Khi nao moi mo rong sang full

Chi mo rong khi:

1. Pha A pass
2. Pha B pass
3. Pha C pass
4. Pha D pass

Neu 4 pha nay da pass, luc do moi chay:

- `hard_bridge_500_validation.csv`
- ablation full
- stress suite
- transfer eval
- theorem-aligned suite

## 7. Lenh full sau khi mini da thong

### 7.1. Ablation full

```powershell
python .\scripts\run_ablation_suite.py --agent react
python .\scripts\run_ablation_suite.py --agent reflexion
```

### 7.2. Stress full

```powershell
python .\scripts\run_stress_suite.py --agent react --strategy full --stress noisy --output-path .\eval\data\react_stress_noisy.csv
```

### 7.3. Transfer

```powershell
python .\scripts\run_transfer_eval.py --in-domain .\eval\data\ablations\react_full.csv --out-of-domain .\eval\data\react_stress_noisy.csv --output-path .\eval\data\react_transfer_summary.csv
```

### 7.4. Theorem-aligned suite

```powershell
python .\scripts\run_theorem_experiment_suite.py --agent react --data-path .\eval\data\hard_bridge_500_validation.csv --output-dir .\experiments\react_theorem_suite --annotations-path .\experiments\react_full_annotations.json
```

## 8. Neu ban muon dung UI thay vi CLI

```powershell
python .\scripts\run_control_panel.py
```

Mo:

```text
http://127.0.0.1:8787
```

Nhung loi khuyen cua toi van la:

- lan dau tien nen chay bang CLI
- khi da thong luong roi moi chuyen sang UI

## 9. Lo trinh ngan nhat toi khuyen dung

Neu ban muon cuc ky thuc dung, thi copy dung thu tu nay:

```powershell
cd "F:\Luận văn thạc sĩ\Paper\purpose\Paper1\DualMemoryKG"
conda activate researchpaper
pip install -r requirements.txt
python .\scripts\run_test_llm.py
python .\scripts\run_prepare_mini_data.py --size 3
python .\scripts\run_react_smoke.py --limit 1
python .\scripts\run_reflexion_smoke.py --limit 1
docker compose up -d
python .\scripts\run_experiment.py --agent react --mode baseline --strategy heuristic --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_baseline_mini.csv
python .\scripts\run_experiment.py --agent react --mode dual_memory --strategy heuristic --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_heuristic_mini.csv
python .\scripts\run_experiment.py --agent react --mode dual_memory --strategy vector_rag --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_vector_rag_mini.csv
python .\scripts\run_experiment.py --agent react --mode dual_memory --strategy graph_rag --data-path .\eval\data\mini_validation_3.csv --output-path .\eval\data\react_graph_rag_mini.csv
```

Sau khi 4 file CSV mini o tren da co, moi chay graph/ontology/traversal.

## 10. Ket luan

Thu tu dung la:

1. env
2. smoke
3. mini baseline
4. mini dual-memory
5. mini graph
6. mini ontology/traversal
7. mini annotation + figure
8. full run

Neu ban muon, buoc tiep theo toi co the viet them cho ban:

- mot file `RUN_FULL_AFTER_MINI_VI.md` chi de mo rong sau khi mini pass
- hoac patch `docs.md` de link thang den tai lieu nay
