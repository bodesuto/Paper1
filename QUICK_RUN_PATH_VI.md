# Lo Trinh Chay That: Tu Mini Den Full

Tai lieu nay danh cho truong hop ban muon:

- chay dung repo theo thu tu it rui ro nhat
- dung du lieu nho truoc de thong luong
- giam quota Gemini va thoi gian debug
- sau khi on moi chuyen sang full experiment

## Pha 1. Mini smoke

```powershell
python .\scripts\run_test_llm.py
python .\scripts\run_prepare_mini_data.py --size 3
python .\scripts\run_react_smoke.py --limit 1
python .\scripts\run_reflexion_smoke.py --limit 1
```

Neu 4 buoc nay on, ban da xac minh duoc:

- Gemini dung duoc
- import va prompt dung
- ReAct/Reflexion co ban khong vo

## Pha 2. Mini graph run

Bat local services:

```powershell
docker compose up -d
docker compose --profile langfuse up -d
```

Bat tracing trong `.env`:

```env
LANGFUSE_TRACING_ENABLED=true
```

Tao trace va chay pipeline graph:

```powershell
python .\scripts\run_react_smoke.py --limit 1
python .\scripts\run_reflexion_smoke.py --limit 1
python .\scripts\run_export.py
python .\scripts\run_format_trace.py
python .\scripts\run_rca.py
python .\scripts\run_kbv.py
python .\scripts\run_hil_streamlit.py
python .\scripts\run_classify.py
python .\scripts\run_insert_obs.py
python .\scripts\run_build_ontology_dataset.py
python .\scripts\run_fit_ontology_prototypes.py
python .\scripts\run_insert_obs.py
python .\scripts\run_react_learned.py
python .\scripts\run_build_policy_dataset.py --input-path .\eval\data\react_learned.csv
python .\scripts\run_fit_traversal_policy.py
```

Artifacts chinh:

- `.\output\langfuse_export.json`
- `.\output\langfuse_export.ontology_dataset.json`
- `.\output\langfuse_export.ontology_prototypes.json`
- `.\output\langfuse_export.traversal_policy_dataset.json`
- `.\output\langfuse_export.traversal_policy.json`

## Pha 3. Full experiment

```powershell
python .\scripts\run_ablation_suite.py --agent react
python .\scripts\run_ablation_suite.py --agent reflexion
python .\scripts\run_stress_suite.py --agent react --strategy full --stress noisy --output-path .\eval\data\react_stress_noisy.csv
python .\scripts\run_transfer_eval.py --in-domain .\eval\data\ablations\react_full.csv --out-of-domain .\eval\data\reflexion_full.csv --output-path .\eval\data\transfer_summary.csv
python .\scripts\run_result_summary.py --inputs .\eval\data\ablations\react_baseline.csv .\eval\data\ablations\react_full.csv .\eval\data\ablations\reflexion_baseline.csv .\eval\data\ablations\reflexion_full.csv --output-path .\eval\data\paper_summary.csv
```

## Bo lenh ngan nhat toi khuyen ban chay

```powershell
python .\scripts\run_test_llm.py
python .\scripts\run_prepare_mini_data.py --size 3
python .\scripts\run_react_smoke.py --limit 1
python .\scripts\run_reflexion_smoke.py --limit 1
docker compose up -d
docker compose --profile langfuse up -d
python .\scripts\run_export.py
python .\scripts\run_format_trace.py
python .\scripts\run_rca.py
python .\scripts\run_kbv.py
python .\scripts\run_hil_streamlit.py
python .\scripts\run_classify.py
python .\scripts\run_insert_obs.py
python .\scripts\run_build_ontology_dataset.py
python .\scripts\run_fit_ontology_prototypes.py
python .\scripts\run_react_learned.py
python .\scripts\run_build_policy_dataset.py --input-path .\eval\data\react_learned.csv
python .\scripts\run_fit_traversal_policy.py
python .\scripts\run_ablation_suite.py --agent react
python .\scripts\run_ablation_suite.py --agent reflexion
python .\scripts\run_result_summary.py --inputs .\eval\data\ablations\react_baseline.csv .\eval\data\ablations\react_full.csv .\eval\data\ablations\reflexion_baseline.csv .\eval\data\ablations\reflexion_full.csv --output-path .\eval\data\paper_summary.csv
```

## Khi nao moi nen chay full

Chi nen chay full khi:

- `run_test_llm.py` da on
- `run_react_smoke.py` da on
- `run_reflexion_smoke.py` da on
- `run_insert_obs.py` da on
- da co file ontology prototypes
- da co file traversal policy
