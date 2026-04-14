import json
from pathlib import Path
from datetime import datetime
from uuid import UUID

from langsmith import Client
from common.logger import get_logger

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


def run_to_dict(run):
    """Flatten LangSmith Run into a JSON-safe dictionary (recursive for child runs)."""
    return {
        "id": str(run.id),
        "parent_run_id": str(run.parent_run_id) if run.parent_run_id else None,
        "name": run.name,
        "type": run.run_type,
        "run_type": run.run_type,
        "inputs": run.inputs,
        "outputs": run.outputs,
        "error": run.error,
        "status": run.status,
        "start_time": run.start_time.isoformat() if run.start_time else None,
        "end_time": run.end_time.isoformat() if run.end_time else None,
        "child_runs": [run_to_dict(c) for c in getattr(run, "child_runs", []) or []],
    }


def export_runs(
    project_id: str | None,
    project_name: str | None,
    output_path: str,
    include_stats: bool = False,
    include_total_stats: bool = False,
):
   
    client = Client()
    if project_id:
        logger.info("Fetching runs for project_id=%s", project_id)
        runs = client.list_runs(project_id=project_id)
    elif project_name:
        logger.info("Fetching runs for project_name=%s", project_name)
        runs = client.list_runs(project_name=project_name)
    else:
        raise ValueError("Either project_id or project_name must be provided.")

    parent_run_ids = []
    for r in runs:
        if r.parent_run_id is None:
            parent_run_ids.append(r.id)
    logger.info("Found %d parent runs", len(parent_run_ids))

    episodes = []
    for rid in parent_run_ids:
        logger.debug("Reading run_id=%s", rid)
        run = client.read_run(run_id=rid, load_child_runs=True)

        ep = run_to_dict(run)

        if include_stats:
            try:
                ep["stats"] = client.get_run_stats(id=[rid])
            except Exception as e:
                logger.warning("Failed to fetch stats for run_id=%s: %s", rid, e)
                ep["stats_error"] = str(e)

        episodes.append(ep)

    payload = {"episodes": episodes}

    if include_total_stats:
        try:
            payload["total_stats"] = client.get_run_stats(id=parent_run_ids)
        except Exception as e:
            logger.warning("Failed to fetch total_stats: %s", e)
            payload["total_stats_error"] = str(e)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    logger.info("Saving export to %s", output_path)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=safe_json)

    logger.info("Export complete. Saved %d episodes.", len(episodes))
