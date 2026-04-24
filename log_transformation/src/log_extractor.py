import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

from common.logger import get_logger
from common.observability import get_langfuse_client, langfuse_is_enabled

logger = get_logger(__name__)


def safe_json(obj):
    """Safely convert non-serializable objects for JSON dumping."""
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)


def _stringify_io(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)


def _normalize_run_type(observation) -> tuple[str, str, dict[str, str]]:
    obs_type = str(getattr(observation, "type", "") or "").lower()
    name = getattr(observation, "name", None) or "observation"
    output_text = _stringify_io(getattr(observation, "output", None))

    if obs_type == "generation":
        return "chain", "LLMChain", {"text": output_text}

    if obs_type in {"tool", "retriever"}:
        return "tool", name, {"output": output_text}

    if any(label in output_text for label in ("Thought:", "Action:", "Final Answer:")):
        return "chain", "LLMChain", {"text": output_text}

    return "tool", name, {"output": output_text}


def _observation_to_run_dict(observation):
    run_type, name, outputs = _normalize_run_type(observation)
    status_message = getattr(observation, "status_message", None)
    level = str(getattr(observation, "level", "") or "").upper()
    return {
        "id": str(getattr(observation, "id", "")),
        "parent_run_id": str(getattr(observation, "parent_observation_id", "") or "") or None,
        "name": name,
        "type": run_type,
        "run_type": run_type,
        "inputs": {"input": _stringify_io(getattr(observation, "input", None))},
        "outputs": outputs,
        "error": status_message if level == "ERROR" else None,
        "status": "error" if level == "ERROR" else "success",
        "start_time": observation.start_time.isoformat() if getattr(observation, "start_time", None) else None,
        "end_time": observation.end_time.isoformat() if getattr(observation, "end_time", None) else None,
        "child_runs": [],
    }


def _sort_child_runs(run: dict) -> None:
    run["child_runs"].sort(key=lambda item: item.get("start_time") or "")
    for child in run["child_runs"]:
        _sort_child_runs(child)


def _build_child_run_tree(observations) -> list[dict]:
    included = [_observation_to_run_dict(observation) for observation in observations or []]
    run_map = {run["id"]: run for run in included if run.get("id")}
    root_runs: list[dict] = []

    for run in included:
        parent_run_id = run.get("parent_run_id")
        if parent_run_id and parent_run_id in run_map:
            run_map[parent_run_id]["child_runs"].append(run)
        else:
            root_runs.append(run)

    root_runs.sort(key=lambda item: item.get("start_time") or "")
    for root in root_runs:
        _sort_child_runs(root)
    return root_runs


def trace_to_dict(trace):
    observations = getattr(trace, "observations", []) or []
    return {
        "id": str(trace.id),
        "parent_run_id": None,
        "name": trace.name or "LangfuseTrace",
        "type": "chain",
        "run_type": "chain",
        "inputs": {"input": _stringify_io(getattr(trace, "input", None))},
        "outputs": {"output": _stringify_io(getattr(trace, "output", None))},
        "error": None,
        "status": "success",
        "start_time": trace.timestamp.isoformat() if getattr(trace, "timestamp", None) else None,
        "end_time": None,
        "child_runs": _build_child_run_tree(observations),
        "tags": list(getattr(trace, "tags", []) or []),
        "metadata": getattr(trace, "metadata", None),
        "environment": getattr(trace, "environment", None),
    }


def export_runs(
    *,
    output_path: str,
    trace_name: str | None = None,
    environment: str | None = None,
    limit: int = 100,
):
    if not langfuse_is_enabled():
        raise ValueError(
            "Langfuse export requires LANGFUSE_TRACING_ENABLED=true plus LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, and LANGFUSE_HOST."
        )

    client = get_langfuse_client()
    if client is None:
        raise RuntimeError("Langfuse client is not available.")

    logger.info("Fetching traces from Langfuse host=%s", getattr(client, "base_url", None) or getattr(client, "host", None) or "configured-host")
    episodes = []
    page = 1
    total_pages = 1

    while page <= total_pages:
        trace_page = client.api.trace.list(
            page=page,
            limit=limit,
            name=trace_name,
            environment=environment,
            fields="core,io",
            order_by="timestamp.desc",
        )
        total_pages = trace_page.meta.total_pages or 1
        logger.info("Fetched Langfuse trace page %d/%d (%d items)", page, total_pages, len(trace_page.data))

        for trace_stub in trace_page.data:
            trace = client.api.trace.get(trace_stub.id, fields="core,io,observations")
            episodes.append(trace_to_dict(trace))

        page += 1

    payload = {"episodes": episodes}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    logger.info("Saving Langfuse export to %s", output_path)

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=safe_json)

    logger.info("Langfuse export complete. Saved %d episodes.", len(episodes))
