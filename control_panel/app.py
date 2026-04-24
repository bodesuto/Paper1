from __future__ import annotations

import os
import subprocess
import threading
import time
import uuid
from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from control_panel.task_catalog import REPO_ROOT, build_runtime_context, get_task_specs


STATIC_DIR = REPO_ROOT / "control_panel" / "static"
ENV_FILE = REPO_ROOT / ".env"
ENV_EXAMPLE_FILE = REPO_ROOT / ".env.example"
TASKS = {task.task_id: task for task in get_task_specs(build_runtime_context(REPO_ROOT))}
PREVIEWABLE_SUFFIXES = {".txt", ".md", ".json", ".csv", ".log", ".yaml", ".yml", ".env"}
PREFERRED_METRIC_COLUMNS = [
    "exact_match",
    "exact_match_eval",
    "f1",
    "unsupported_reasoning_score",
    "path_grounding_precision",
    "path_grounding_recall",
    "path_grounding_f1",
    "evidence_precision",
    "evidence_recall",
    "latency_seconds",
    "tool_calls",
]
ENV_FIELD_SPECS = [
    {
        "name": "LOG_LEVEL",
        "label": "Log level",
        "group": "General",
        "description": "Application logging verbosity.",
        "sensitive": False,
    },
    {
        "name": "GOOGLE_API_KEY",
        "label": "Google API key",
        "group": "Gemini",
        "description": "Preferred Gemini key. If both keys exist, this one wins.",
        "sensitive": True,
    },
    {
        "name": "GEMINI_API_KEY",
        "label": "Gemini API key",
        "group": "Gemini",
        "description": "Fallback alias if GOOGLE_API_KEY is blank.",
        "sensitive": True,
    },
    {
        "name": "GEMINI_MODEL_NAME",
        "label": "Gemini model",
        "group": "Gemini",
        "description": "Primary chat model for repo execution.",
        "sensitive": False,
    },
    {
        "name": "GEMINI_EMBEDDING_MODEL",
        "label": "Embedding model",
        "group": "Gemini",
        "description": "Embedding model used for graph/vector retrieval.",
        "sensitive": False,
    },
    {
        "name": "EMBEDDING_VECTOR_DIMENSIONS",
        "label": "Embedding dimensions",
        "group": "Gemini",
        "description": "Optional fixed vector dimension for Neo4j index creation.",
        "sensitive": False,
    },
    {
        "name": "LANGFUSE_TRACING_ENABLED",
        "label": "Langfuse tracing",
        "group": "Langfuse",
        "description": "Enable or disable Langfuse tracing callbacks.",
        "sensitive": False,
    },
    {
        "name": "LANGFUSE_HOST",
        "label": "Langfuse host",
        "group": "Langfuse",
        "description": "Base URL of the Langfuse instance, for example http://localhost:3000.",
        "sensitive": False,
    },
    {
        "name": "LANGFUSE_PUBLIC_KEY",
        "label": "Langfuse public key",
        "group": "Langfuse",
        "description": "Project-scoped Langfuse public key used by tracing and export.",
        "sensitive": False,
    },
    {
        "name": "LANGFUSE_SECRET_KEY",
        "label": "Langfuse secret key",
        "group": "Langfuse",
        "description": "Project-scoped Langfuse secret key used by tracing and export.",
        "sensitive": True,
    },
    {
        "name": "LANGFUSE_ENVIRONMENT",
        "label": "Langfuse environment",
        "group": "Langfuse",
        "description": "Optional environment tag used when exporting traces.",
        "sensitive": False,
    },
    {
        "name": "LANGFUSE_RELEASE",
        "label": "Langfuse release",
        "group": "Langfuse",
        "description": "Optional release tag stored on traces.",
        "sensitive": False,
    },
    {
        "name": "LANGFUSE_TRACE_NAME",
        "label": "Langfuse trace name",
        "group": "Langfuse",
        "description": "Optional export filter for trace name.",
        "sensitive": False,
    },
    {
        "name": "OUTPUT_PATH",
        "label": "Output path",
        "group": "Paths",
        "description": "Base output file used by export and downstream pipeline stages.",
        "sensitive": False,
    },
    {
        "name": "DATA_PATH",
        "label": "Data path",
        "group": "Paths",
        "description": "Folder containing evaluation CSV files.",
        "sensitive": False,
    },
    {
        "name": "CONFIDENT_API_KEY",
        "label": "Confident API key",
        "group": "Evaluation",
        "description": "Used by DeepEval/KBV stages when required.",
        "sensitive": True,
    },
    {
        "name": "RETRIEVAL_STRATEGY",
        "label": "Retrieval strategy",
        "group": "Retrieval",
        "description": "Default retrieval mode for experiment scripts.",
        "sensitive": False,
    },
    {
        "name": "ONTOLOGY_PROTOTYPES_PATH",
        "label": "Ontology prototypes path",
        "group": "Retrieval",
        "description": "Learned ontology prototype file.",
        "sensitive": False,
    },
    {
        "name": "ONTOLOGY_TOP_K",
        "label": "Ontology top-k",
        "group": "Retrieval",
        "description": "How many ontology candidates to retain.",
        "sensitive": False,
    },
    {
        "name": "LEARNED_RETRIEVAL_TOP_K",
        "label": "Learned retrieval top-k",
        "group": "Retrieval",
        "description": "How many learned retrieval candidates to keep.",
        "sensitive": False,
    },
    {
        "name": "TRAVERSAL_POLICY_PATH",
        "label": "Traversal policy path",
        "group": "Retrieval",
        "description": "Learned traversal ranking policy file.",
        "sensitive": False,
    },
    {
        "name": "TRAVERSAL_TOP_K",
        "label": "Traversal top-k",
        "group": "Retrieval",
        "description": "How many graph paths to score downstream.",
        "sensitive": False,
    },
    {
        "name": "NEO4J_URI",
        "label": "Neo4j URI",
        "group": "Neo4j",
        "description": "Neo4j connection string.",
        "sensitive": False,
    },
    {
        "name": "NEO4J_USER",
        "label": "Neo4j user",
        "group": "Neo4j",
        "description": "Neo4j username.",
        "sensitive": False,
    },
    {
        "name": "NEO4J_PASSWORD",
        "label": "Neo4j password",
        "group": "Neo4j",
        "description": "Neo4j password.",
        "sensitive": True,
    },
    {
        "name": "NEO4J_DATABASE",
        "label": "Neo4j database",
        "group": "Neo4j",
        "description": "Database name used by the repo.",
        "sensitive": False,
    },
]


@dataclass
class JobState:
    job_id: str
    task_id: str
    task_title: str
    status: str
    created_at: float
    params: dict[str, object] = field(default_factory=dict)
    commands: list[list[str]] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)
    return_code: int | None = None
    started_at: float | None = None
    ended_at: float | None = None
    expected_outputs: list[str] = field(default_factory=list)
    manual: bool = False
    caution: str = ""
    cancel_requested: bool = False

    def append_log(self, line: str) -> None:
        self.logs.append(line.rstrip("\n"))
        if len(self.logs) > 1600:
            self.logs = self.logs[-1600:]


class RunTaskRequest(BaseModel):
    task_id: str
    params: dict[str, object] = Field(default_factory=dict)


class EnvUpdateRequest(BaseModel):
    values: dict[str, str] = Field(default_factory=dict)


app = FastAPI(title="DualMemoryKG Control Panel")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

_jobs: dict[str, JobState] = {}
_job_lock = threading.Lock()
_active_job_id: str | None = None
_queued_job_ids: deque[str] = deque()
_queue_event = threading.Event()
_job_processes: dict[str, subprocess.Popen[str]] = {}


def _resolve_repo_path(raw_path: str | Path) -> Path:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(REPO_ROOT.resolve())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Path is outside repository: {raw_path}") from exc
    return resolved


def _display_repo_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def _artifact_info(path: Path) -> dict[str, object]:
    exists = path.exists()
    return {
        "path": _display_repo_path(path),
        "exists": exists,
        "is_dir": path.is_dir() if exists else False,
        "size_bytes": path.stat().st_size if exists and path.is_file() else None,
        "modified_at": path.stat().st_mtime if exists else None,
    }


def _job_to_payload(job: JobState) -> dict[str, object]:
    payload = asdict(job)
    payload["logs"] = job.logs[-500:]
    payload["artifacts"] = [_artifact_info(_resolve_repo_path(path)) for path in job.expected_outputs]
    payload["queue_position"] = list(_queued_job_ids).index(job.job_id) + 1 if job.job_id in _queued_job_ids else None
    payload["is_active"] = job.job_id == _active_job_id
    return payload


def _load_env_values(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values = dotenv_values(path)
    return {str(key): "" if value is None else str(value) for key, value in values.items() if key}


def _merge_env_values() -> dict[str, str]:
    merged = _load_env_values(ENV_EXAMPLE_FILE)
    merged.update(_load_env_values(ENV_FILE))
    return merged


def _serialize_env_value(value: str) -> str:
    if value == "":
        return ""
    if any(char.isspace() for char in value) or any(char in value for char in ['"', "#", "\n", "\r"]):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def _env_fields_payload() -> list[dict[str, object]]:
    values = _merge_env_values()
    return [
        {
            "name": spec["name"],
            "label": spec["label"],
            "group": spec["group"],
            "description": spec["description"],
            "sensitive": spec["sensitive"],
            "value": values.get(spec["name"], ""),
        }
        for spec in ENV_FIELD_SPECS
    ]


def _write_env_values(new_values: dict[str, str]) -> None:
    existing = _load_env_values(ENV_FILE)
    example_defaults = _load_env_values(ENV_EXAMPLE_FILE)
    merged = {**example_defaults, **existing}
    for spec in ENV_FIELD_SPECS:
        name = spec["name"]
        merged[name] = str(new_values.get(name, ""))

    lines: list[str] = []
    current_group = None
    for spec in ENV_FIELD_SPECS:
        group = str(spec["group"])
        if group != current_group:
            if lines:
                lines.append("")
            lines.append(f"# {group}")
            current_group = group
        name = str(spec["name"])
        description = str(spec["description"])
        lines.append(f"# {description}")
        lines.append(f"{name}={_serialize_env_value(merged.get(name, ''))}")

    known_names = {str(spec["name"]) for spec in ENV_FIELD_SPECS}
    extras = {key: value for key, value in existing.items() if key not in known_names}
    if extras:
        lines.append("")
        lines.append("# Extra")
        for key in sorted(extras):
            lines.append(f"{key}={_serialize_env_value(extras[key])}")

    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _env_status() -> dict[str, object]:
    env_values = build_runtime_context(REPO_ROOT).env_values
    google_present = bool(env_values.get("GOOGLE_API_KEY"))
    gemini_present = bool(env_values.get("GEMINI_API_KEY"))
    neo4j_present = all(env_values.get(name) for name in ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"))
    langfuse_present = bool(env_values.get("LANGFUSE_PUBLIC_KEY") and env_values.get("LANGFUSE_SECRET_KEY"))
    return {
        "env_file_exists": ENV_FILE.exists(),
        "google_api_key": google_present,
        "gemini_api_key": gemini_present,
        "langfuse_config": langfuse_present,
        "neo4j_credentials": neo4j_present,
        "effective_output_path": str(build_runtime_context(REPO_ROOT).output_path),
        "effective_data_path": str(build_runtime_context(REPO_ROOT).data_path),
        "retrieval_strategy": env_values.get("RETRIEVAL_STRATEGY", ""),
    }


def _list_common_artifacts() -> list[dict[str, object]]:
    ctx = build_runtime_context(REPO_ROOT)
    candidates = [
        ctx.output_path,
        ctx.output_path.with_suffix(".react.txt"),
        ctx.output_path.with_suffix(".rca.json"),
        ctx.output_path.with_suffix(".kbv.json"),
        ctx.output_path.with_suffix(".hil.json"),
        ctx.output_path.with_suffix(".classified.json"),
        ctx.output_path.with_suffix(".classified_insights.json"),
        ctx.output_path.with_suffix(".ontology_dataset.json"),
        ctx.output_path.with_suffix(".ontology_prototypes.json"),
        ctx.output_path.with_suffix(".traversal_policy_dataset.json"),
        ctx.output_path.with_suffix(".traversal_policy.json"),
        ctx.data_path,
        ctx.data_path / "react_smoke_results.csv",
        ctx.data_path / "reflexion_smoke_results.csv",
        ctx.data_path / "react_learned.csv",
        ctx.data_path / "react_full.csv",
        ctx.data_path / "reflexion_full.csv",
        ctx.data_path / "ablations",
        REPO_ROOT / "output",
    ]
    return [_artifact_info(path) for path in candidates]


def _mark_job_cancelled(job: JobState, return_code: int | None = None) -> None:
    job.status = "cancelled"
    job.return_code = return_code
    job.ended_at = time.time()


def _run_job(job: JobState) -> None:
    job.status = "running"
    job.started_at = time.time()

    try:
        for step_index, command in enumerate(job.commands, start=1):
            if job.cancel_requested:
                _mark_job_cancelled(job)
                job.append_log("[cancelled] job was cancelled before execution started")
                return

            label = " ".join(command[1:]) if len(command) > 1 else command[0]
            job.append_log(f"[step {step_index}/{len(job.commands)}] {label}")
            process = subprocess.Popen(
                command,
                cwd=REPO_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=os.environ.copy(),
            )

            with _job_lock:
                _job_processes[job.job_id] = process

            while True:
                line = process.stdout.readline() if process.stdout is not None else ""
                if line:
                    job.append_log(line.rstrip("\n"))
                if process.poll() is not None:
                    break

            if process.stdout is not None:
                remainder = process.stdout.read()
                if remainder:
                    for line in remainder.splitlines():
                        job.append_log(line)

            return_code = process.wait()
            with _job_lock:
                _job_processes.pop(job.job_id, None)

            if job.cancel_requested:
                _mark_job_cancelled(job, return_code)
                job.append_log(f"[cancelled] running subprocess stopped with code {return_code}")
                return

            if return_code != 0:
                job.status = "failed"
                job.return_code = return_code
                job.append_log(f"[error] command exited with code {return_code}")
                return

        job.status = "completed"
        job.return_code = 0
        job.append_log("[done] task completed successfully")
    except Exception as exc:
        if job.cancel_requested:
            _mark_job_cancelled(job, job.return_code)
            job.append_log(f"[cancelled] {type(exc).__name__}: {exc}")
        else:
            job.status = "failed"
            job.return_code = -1
            job.append_log(f"[exception] {type(exc).__name__}: {exc}")
    finally:
        with _job_lock:
            _job_processes.pop(job.job_id, None)
        if job.ended_at is None:
            job.ended_at = time.time()


def _queue_worker() -> None:
    global _active_job_id
    while True:
        _queue_event.wait()
        next_job: JobState | None = None
        with _job_lock:
            if _active_job_id is None and _queued_job_ids:
                job_id = _queued_job_ids.popleft()
                next_job = _jobs.get(job_id)
                _active_job_id = job_id if next_job else None
            if not _queued_job_ids and _active_job_id is None:
                _queue_event.clear()
        if next_job is None:
            continue
        next_job.status = "starting"
        next_job.append_log("[queued] picked up by worker")
        _run_job(next_job)
        with _job_lock:
            _active_job_id = None
            if _queued_job_ids:
                _queue_event.set()
            else:
                _queue_event.clear()


def _start_worker_once() -> None:
    worker = threading.Thread(target=_queue_worker, daemon=True, name="control-panel-worker")
    worker.start()


def _list_directory_entries(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    entries = []
    for child in sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
        entries.append(_artifact_info(child))
    return entries


def _read_preview(path: Path, max_chars: int = 6000) -> str:
    if not path.exists() or path.is_dir():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""


def _json_safe_scalar(value: Any) -> Any:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    return value


def _metric_cards_from_frame(frame: pd.DataFrame) -> list[dict[str, object]]:
    numeric_columns = [column for column in frame.columns if pd.api.types.is_numeric_dtype(frame[column])]
    ordered_columns = [column for column in PREFERRED_METRIC_COLUMNS if column in numeric_columns]
    ordered_columns.extend(column for column in numeric_columns if column not in ordered_columns)
    cards = []
    for column in ordered_columns[:8]:
        series = pd.to_numeric(frame[column], errors="coerce").dropna()
        if series.empty:
            continue
        cards.append(
            {
                "name": column,
                "mean": round(float(series.mean()), 4),
                "min": round(float(series.min()), 4),
                "max": round(float(series.max()), 4),
            }
        )
    return cards


@app.get("/api/overview")
def get_overview() -> dict[str, object]:
    ctx = build_runtime_context(REPO_ROOT)
    tasks = []
    for task in get_task_specs(ctx):
        tasks.append(
            {
                "task_id": task.task_id,
                "title": task.title,
                "group": task.group,
                "summary": task.summary,
                "fields": [asdict(field) for field in task.fields],
                "manual": task.manual,
                "featured": task.featured,
                "caution": task.caution,
                "expected_outputs": task.expected_outputs({}, ctx) if task.expected_outputs else [],
            }
        )
    return {
        "tasks": tasks,
        "env_status": _env_status(),
        "artifacts": _list_common_artifacts(),
        "active_job_id": _active_job_id,
        "queued_job_ids": list(_queued_job_ids),
        "artifact_roots": [
            _artifact_info(REPO_ROOT / "output"),
            _artifact_info(ctx.data_path),
            _artifact_info(REPO_ROOT),
        ],
    }


@app.get("/api/jobs")
def list_jobs() -> list[dict[str, object]]:
    return [_job_to_payload(job) for job in sorted(_jobs.values(), key=lambda item: item.created_at, reverse=True)]


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, object]:
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_payload(job)


@app.post("/api/jobs")
def run_task(request: RunTaskRequest) -> dict[str, object]:
    task = TASKS.get(request.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    with _job_lock:
        ctx = build_runtime_context(REPO_ROOT)
        job_id = uuid.uuid4().hex[:12]
        commands = task.command_builder(request.params, ctx)
        expected_outputs = task.expected_outputs(request.params, ctx) if task.expected_outputs else []
        job = JobState(
            job_id=job_id,
            task_id=task.task_id,
            task_title=task.title,
            status="queued",
            created_at=time.time(),
            params=request.params,
            commands=commands,
            expected_outputs=expected_outputs,
            manual=task.manual,
            caution=task.caution,
        )
        job.append_log(f"[queued] {task.title}")
        if task.caution:
            job.append_log(f"[note] {task.caution}")
        _jobs[job_id] = job
        _queued_job_ids.append(job_id)
        _queue_event.set()

    return _job_to_payload(job)


@app.post("/api/jobs/{job_id}/cancel")
def cancel_job(job_id: str) -> dict[str, object]:
    process: subprocess.Popen[str] | None = None

    with _job_lock:
        job = _jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status in {"completed", "failed", "cancelled"}:
            return _job_to_payload(job)

        job.cancel_requested = True

        if job_id in _queued_job_ids:
            _queued_job_ids.remove(job_id)
            _mark_job_cancelled(job)
            job.append_log("[cancelled] removed from queue")
            if not _queued_job_ids and _active_job_id is None:
                _queue_event.clear()
            return _job_to_payload(job)

        process = _job_processes.get(job_id)
        if process is None:
            _mark_job_cancelled(job)
            job.append_log("[cancelled] job was marked as cancelled")
            return _job_to_payload(job)

        job.append_log("[cancel] termination requested for running subprocess")

    try:
        process.terminate()
    except Exception as exc:
        with _job_lock:
            job = _jobs.get(job_id)
            if job:
                job.append_log(f"[cancel-warning] terminate failed: {exc}")
        try:
            process.kill()
        except Exception as kill_exc:
            raise HTTPException(status_code=500, detail=f"Failed to cancel job: {kill_exc}") from kill_exc

    try:
        process.wait(timeout=4)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=4)
        with _job_lock:
            job = _jobs.get(job_id)
            if job:
                job.append_log("[cancel] process did not stop on terminate; kill was used")

    with _job_lock:
        job = _jobs.get(job_id)
        if job and job.status not in {"completed", "failed", "cancelled"}:
            _mark_job_cancelled(job, process.returncode)
            job.append_log(f"[cancelled] subprocess ended with code {process.returncode}")
    if not job:
        raise HTTPException(status_code=404, detail="Job not found after cancellation")
    return _job_to_payload(job)


@app.post("/api/tasks/preview")
def preview_task_outputs(request: RunTaskRequest) -> dict[str, object]:
    task = TASKS.get(request.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    ctx = build_runtime_context(REPO_ROOT)
    outputs = task.expected_outputs(request.params, ctx) if task.expected_outputs else []
    return {"expected_outputs": outputs}


@app.get("/api/env")
def get_env_config() -> dict[str, object]:
    return {
        "env_file_exists": ENV_FILE.exists(),
        "env_file_path": _display_repo_path(ENV_FILE),
        "fields": _env_fields_payload(),
        "env_status": _env_status(),
    }


@app.post("/api/env")
def save_env_config(request: EnvUpdateRequest) -> dict[str, object]:
    _write_env_values(request.values)
    return {
        "saved": True,
        "env_file_path": _display_repo_path(ENV_FILE),
        "fields": _env_fields_payload(),
        "env_status": _env_status(),
    }


@app.get("/api/artifacts")
def browse_artifacts(path: str | None = Query(default=None)) -> dict[str, object]:
    target = _resolve_repo_path(path or ".")
    parent = target.parent if target != REPO_ROOT else None
    return {
        "current": _artifact_info(target),
        "parent": _artifact_info(parent) if parent and parent != target else None,
        "children": _list_directory_entries(target) if target.exists() and target.is_dir() else [],
    }


@app.get("/api/artifacts/preview")
def preview_artifact(path: str = Query(...)) -> dict[str, object]:
    target = _resolve_repo_path(path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    if target.is_dir():
        return {
            "artifact": _artifact_info(target),
            "kind": "directory",
            "children": _list_directory_entries(target),
            "content": "",
        }
    suffix = target.suffix.lower()
    preview = _read_preview(target) if suffix in PREVIEWABLE_SUFFIXES else ""
    return {
        "artifact": _artifact_info(target),
        "kind": "file",
        "children": [],
        "content": preview,
        "download_url": f"/api/artifacts/download?path={_artifact_info(target)['path']}",
    }


@app.get("/api/results/preview")
def preview_results(path: str = Query(...), row_limit: int = Query(default=20, ge=1, le=100)) -> dict[str, object]:
    target = _resolve_repo_path(path)
    if not target.exists() or target.is_dir():
        raise HTTPException(status_code=404, detail="Result file not found")
    if target.suffix.lower() != ".csv":
        raise HTTPException(status_code=400, detail="Result preview currently supports CSV files only")

    try:
        frame = pd.read_csv(target)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {exc}") from exc

    rows = []
    for _, row in frame.head(row_limit).iterrows():
        rows.append({column: _json_safe_scalar(value) for column, value in row.to_dict().items()})

    return {
        "artifact": _artifact_info(target),
        "summary": {
            "row_count": int(len(frame)),
            "column_count": int(len(frame.columns)),
            "columns": [str(column) for column in frame.columns],
        },
        "metric_cards": _metric_cards_from_frame(frame),
        "rows": rows,
    }


@app.get("/api/artifacts/download")
def download_artifact(path: str = Query(...)) -> FileResponse:
    target = _resolve_repo_path(path)
    if not target.exists() or target.is_dir():
        raise HTTPException(status_code=404, detail="Artifact file not found")
    return FileResponse(target)


@app.post("/api/artifacts/open-folder")
def open_artifact_folder(path: str = Query(...)) -> dict[str, object]:
    target = _resolve_repo_path(path)
    folder = target if target.is_dir() else target.parent
    if not folder.exists():
        raise HTTPException(status_code=404, detail="Folder not found")
    try:
        if os.name == "nt":
            subprocess.Popen(["explorer", str(folder)])
        else:
            raise HTTPException(status_code=400, detail="Open folder is only implemented for Windows in this control panel.")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to open folder: {exc}") from exc
    return {"opened": str(folder)}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


_start_worker_once()
