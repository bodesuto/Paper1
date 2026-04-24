# DualMemoryKG

Implementation repo for:

> **Matharaarachchi et al., 2026 - Knowledge-Based Systems**  
> *Addressing Hallucinations in Generative AI Agents using Observability and Dual Memory Knowledge Graphs*

Repo này hiện có 2 lớp:

1. phần tái hiện pipeline gốc của bài báo
2. phần mở rộng theo `proposal.md` để tiến tới paper mạnh hơn

## Đọc tài liệu theo thứ tự

- [QUICK_RUN_PATH_VI.md](./QUICK_RUN_PATH_VI.md): lộ trình chạy thật ngắn nhất từ mini đến full
- [RUN_MINI_FIRST_VI.md](./RUN_MINI_FIRST_VI.md): tài liệu từng bước một, ưu tiên thông luồng trên dữ liệu nhỏ trước
- [REPRODUCTION_GUIDE_VI.md](./REPRODUCTION_GUIDE_VI.md): hướng dẫn đầy đủ từ cài đặt đến chạy toàn bộ repo
- [CONTRIBUTIONS_AND_STATUS_VI.md](./CONTRIBUTIONS_AND_STATUS_VI.md): repo hiện đã đóng góp mới gì, phần nào đã implement, phần nào mới ở mức mở rộng hợp lý
- [TROUBLESHOOTING_VI.md](./TROUBLESHOOTING_VI.md): lỗi thường gặp và cách xử lý
- [RUN_ORDER.md](./RUN_ORDER.md): thứ tự lệnh ngắn gọn
- [PAPER_EXPERIMENT_CHECKLIST.md](./PAPER_EXPERIMENT_CHECKLIST.md): checklist paper-facing
- [scripts/README.md](./scripts/README.md): mô tả nhanh từng script

## Mục tiêu của repo hiện tại

Repo hỗ trợ:

- ReAct baseline
- Reflexion baseline
- dual-memory knowledge graph với Neo4j
- heuristic retrieval
- vector-RAG baseline
- graph-aware proxy baseline
- ontology-only ablation
- traversal-only ablation
- learned mode
- full mode
- grounding metrics
- stress tests
- transfer summaries
- result summary tables
- local control panel để chạy các bước bằng giao diện web

## Cấu trúc chính

```text
agents/               # ReAct + Reflexion agents
classifier/           # Intent / entity / attribute classification
common/               # Shared config, Gemini models, logging
data_pipeline/        # Build datasets for ontology / traversal training
diagnostics/          # RCA, KBV, HIL
eval/                 # Evaluation and grounding metrics
knowledge_graph/      # Neo4j graph schema, insert, retrieval
log_transformation/   # Langfuse/export -> ReAct trace pipeline
reasoning_ontology/   # Ontology dataset, encoder, prototype learner, inference
scripts/              # All runnable entry points
traversal_policy/     # Traversal dataset, training, inference
```

## Quick start rất ngắn

1. Tạo môi trường và cài package:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

2. Tạo `.env` từ `.env.example`

3. Test LLM:

```powershell
python .\scripts\run_test_llm.py
```

4. Nếu muốn thao tác bằng giao diện thay vì gõ lệnh:

```powershell
python .\scripts\run_control_panel.py
```

Mở trình duyệt tại:

```text
http://127.0.0.1:8787
```

Control panel hiện hỗ trợ:

- queue nhiều job thay vì chạy từng lệnh riêng lẻ
- task presets cho smoke, graph bootstrap, learned stack, ablation, stress, summary
- live logs cho từng job
- hủy job đang chạy hoặc còn nằm trong queue
- chỉnh trực tiếp `.env` ngay trên UI
- artifact browser + preview file/thư mục ngay trong UI
- đọc nhanh CSV kết quả với metric cards và bảng preview
- mở thư mục kết quả từ UI trên Windows

5. Chạy smoke test giá rẻ:

```powershell
python .\scripts\run_prepare_mini_data.py --size 3
python .\scripts\run_react_smoke.py --limit 1
python .\scripts\run_reflexion_smoke.py --limit 1
```

6. Nếu muốn tái hiện đầy đủ, chuyển sang [REPRODUCTION_GUIDE_VI.md](./REPRODUCTION_GUIDE_VI.md)

## Lưu ý quan trọng

- Repo chấp nhận `GOOGLE_API_KEY` hoặc `GEMINI_API_KEY`
- Nếu cả hai cùng có, code sẽ ưu tiên `GOOGLE_API_KEY`
- `full` mode chỉ thực sự đúng nghĩa khi đã có file `traversal_policy.json`
- Nếu dùng Gemini embeddings với Neo4j vector index, có thể để hệ thống tự probe dimension hoặc tự set `EMBEDDING_VECTOR_DIMENSIONS`
- Phần mở rộng ontology/traversal đã được implement thêm, nhưng bạn nên đọc kỹ [CONTRIBUTIONS_AND_STATUS_VI.md](./CONTRIBUTIONS_AND_STATUS_VI.md) để tránh overclaim khi viết paper
