import re
from datetime import datetime
import json
from pathlib import Path

from common.logger import get_logger

logger = get_logger(__name__)
# ========== UTIL FUNCTIONS ==========

def clean_text(t):
    if not t:
        return ""
    if not isinstance(t, str):
        t = str(t)
    t = t.replace("\\n", "\n").replace("\\xa0", " ").strip()
    return re.sub(r"\s+", " ", t)


def parse_time(s):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return datetime.min


def extract_chain_text(run):
    """Extract reasoning text only from LLMChain outputs."""
    outputs = run.get("outputs", {}) or {}
    if "text" in outputs:
        return clean_text(outputs["text"])
    return ""


def extract_observation(run):
    """Extract tool output text from tool runs."""
    run_type = run.get("type") or run.get("run_type")
    if run_type == "tool":
        out = run.get("outputs", {}).get("output", "")
        return clean_text(out) if out else ""
    return ""


def summarize_observation(obs):
    """Short summary of noisy Wikipedia tool observation."""
    # Extract cast
    m = re.search(r"starring (.*?)(?:\.|$)", obs, re.I)
    if m:
        return f"The film stars {m.group(1)}."

    # Use first Summary sentence
    if "Summary:" in obs:
        part = obs.split("Summary:", 1)[1].strip()
        return part.split(".")[0].strip() + "."

    return obs[:200].strip() + "..."


# ========== MAIN EXTRACTION ==========

def extract_reasoning_trace(run):
    """Extract a ReAct reasoning chain from an exported observability trace."""

    # Sort chronologically
    child_runs = sorted(run.get("child_runs", []),
                        key=lambda r: parse_time(r.get("start_time", "")))

    steps = []

    # Regex for all labeled blocks
    pattern = (
        r"(Thought|Action(?: Input)?|Action|Observation|Final Answer):"
        r"\s*(.*?)(?=(Thought|Action(?: Input)?|Observation|Final Answer):|$)"
    )

    def process_llm_text(text):
        """Extract missing Thought + labeled blocks from LLM text."""
        text = text.strip()
        if not text:
            return

        # -------- 1) Missing-Thought Detection --------
        # If the text DOES NOT START with a label, but includes a free paragraph first
        if not re.match(r"^(Thought|Action(?: Input)?|Observation|Final Answer):", text, re.I):

            # Cut the first unlabeled paragraph BEFORE the first real label
            first_para = re.split(
                r"(Thought|Action(?: Input)?|Observation|Final Answer):",
                text, 1
            )[0]
            first_para = clean_text(first_para)

            if first_para:
                steps.append(("Thought", first_para))

        # -------- 2) Extract explicit labeled blocks --------
        for m in re.finditer(pattern, text, re.S):
            label = m.group(1).strip()
            content = clean_text(m.group(2))

            # Remove inline labels inside Thought blocks
            if label == "Thought":
                content = re.split(
                    r"(Action|Observation|Final Answer):",
                    content, 1
                )[0].strip()

            steps.append((label, content))

    # ========== TRAVERSE RUN TREE ==========

    for r in child_runs:
        run_type = r.get("type") or r.get("run_type")

        # ---------------- LLMChain ----------------
        if run_type == "chain" and r.get("name") == "LLMChain":
            text = extract_chain_text(r)
            process_llm_text(text)

        # ---------------- TOOL CALL ----------------
        elif run_type == "tool":
            obs = extract_observation(r)
            if obs:
                steps.append(("Observation", summarize_observation(obs)))

        # ---------------- NESTED CHAINS ----------------
        for c in r.get("child_runs", []):
            child_type = c.get("type") or c.get("run_type")
            if child_type == "chain" and c.get("name") == "LLMChain":
                text = extract_chain_text(c)
                process_llm_text(text)

    # ========== DEDUPLICATE STEPS ==========

    merged = []
    for label, content in steps:
        if not merged or merged[-1] != (label, content):
            merged.append((label, content))

    # ========== FORMAT OUTPUT ==========

    q = clean_text(run.get("inputs", {}).get("input") or "")
    out = [f"Question: {q}"]

    for label, content in merged:
        out.append(f"{label}: {content}")

    return "\n".join(out)

def load_export_json(path: str | Path):
    """Supports both formats:
      - payload = {"episodes":[...], "total_stats":...}
      - episodes = [...]
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data["episodes"]

def write_react_traces(in_json_path: str | Path, out_txt_path: str | Path):
    episodes = load_export_json(in_json_path)
    logger.info("Loaded %d episodes from %s", len(episodes), in_json_path)

    out_txt_path = Path(out_txt_path)
    out_txt_path.parent.mkdir(parents=True, exist_ok=True)

    extracted_runs = []
    for run in episodes:
        cleaned_round = extract_reasoning_trace(run)
        if cleaned_round.strip():
            extracted_runs.append(cleaned_round)

    with out_txt_path.open("w", encoding="utf-8") as f:
        for item in extracted_runs:
            f.write(item + "\n\n" + "=" * 80 + "\n\n")

    logger.info("Wrote ReAct traces to %s", out_txt_path)
