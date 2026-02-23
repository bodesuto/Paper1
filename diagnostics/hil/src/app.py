import json
from pathlib import Path
from datetime import datetime
import streamlit as st
import sys

# Ensure the repository root (the directory that contains `common`) is on sys.path.
# Walk up the parents and insert the first directory that contains a `common` folder.
p = Path(__file__).resolve()
for parent in p.parents:
    if (parent / "common").is_dir():
        sys.path.insert(0, str(parent))
        break
else:
    # Fallback: insert a reasonable ancestor if `common` wasn't found.
    if len(p.parents) >= 4:
        sys.path.insert(0, str(p.parents[3]))

from common.config import OUTPUT_PATH

st.set_page_config(page_title="HIL Trace Review", layout="wide")


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def atomic_write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


def upsert_review_in_traces(traces_path: Path, trace_key: str, reviewer_id: str, rating: int, comment: str):
    if rating is None:
        raise ValueError("Rating cannot be None")
    
    traces = load_json(traces_path, default=[])
    if not isinstance(traces, list):
        raise ValueError("Traces file must be a JSON list")

    updated = False
    for t in traces:
        key = str(t.get("index", t.get("id")))
        if key == trace_key:
            reviews = t.setdefault("reviews", {})
            reviews[reviewer_id] = {"score": int(rating), "comment": comment or ""}
            # get total reviews and average rating
            total_reviews = len(reviews)
            avg_rating = sum(r["score"] for r in reviews.values()) / total_reviews if total_reviews > 0 else 0
            t["review_score"] = avg_rating
            updated = True
            break

    if not updated:
        # if not found, append a new entry with minimal info
        traces.append({
            "index": int(trace_key) if trace_key.isdigit() else trace_key,
            "question": "",
            "actual_answer": "",
            "trace": "",
            "reviews": {
                reviewer_id: {"score": int(rating), "comment": comment or ""}
            },
            "review_score": 0
        })

    atomic_write_json(traces_path, traces)


def is_submitted_in_trace(t, trace_key: str, reviewer_id: str):
    reviews = t.get("reviews", {})
    return reviewer_id in reviews

def main():
    traces_path = Path(OUTPUT_PATH).with_suffix(".hil.json")

    traces = load_json(traces_path, default=[])
    if not isinstance(traces, list):
        st.error("Traces file must be a JSON list.")
        st.stop()

    reviewer_id = st.sidebar.text_input("Reviewer ID", value="reviewer_1").strip()
    if not reviewer_id:
        st.warning("Enter a Reviewer ID.")
        st.stop()

    # compute pending vs submitted using `index` or `id` as the trace key
    def trace_key_of(t):
        return str(t.get("index", t.get("id")))

    pending = [t for t in traces if not is_submitted_in_trace(t, trace_key_of(t), reviewer_id)]
    submitted = [t for t in traces if is_submitted_in_trace(t, trace_key_of(t), reviewer_id)]

    st.sidebar.write(f"✅ Submitted: {len(submitted)}")
    st.sidebar.write(f"⏳ Pending: {len(pending)}")

    show = st.sidebar.radio("Show", ["Pending first", "Pending only", "Submitted only", "All"], index=0)
    if show == "Pending only":
        listed = pending
    elif show == "Submitted only":
        listed = submitted
    elif show == "All":
        listed = traces
    else:
        listed = pending + submitted

    # left panel: list of questions with flag, score, and clickable
    def label(t):
        tid = trace_key_of(t)
        status = "✅" if is_submitted_in_trace(t, tid, reviewer_id) else "⏳"
        q = t.get("question", "") or t.get("actual_answer", "")
        return f"{status} [{tid}] {q[:90]}"

    options = {label(t): t for t in listed}
    if not options:
        st.info("No traces to show.")
        st.stop()

    selected_label = st.sidebar.selectbox("Select trace", list(options.keys()))
    trace = options[selected_label]
    trace_id = trace_key_of(trace)

    st.subheader("Question")
    st.write(trace.get("question", ""))

    st.subheader("Trace")
    st.code(trace.get("trace", ""), language="text")

    st.divider()
    st.subheader("Your Review")

    # rating as stars, unselected by default
    stars = {None: "Not set", 1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐", 4: "⭐⭐⭐⭐", 5: "⭐⭐⭐⭐⭐"}
    # initialize draft in session_state
    draft_key = f"draft::{reviewer_id}::{trace_id}"
    if draft_key not in st.session_state:
        current = trace.get("reviews", {}).get(reviewer_id, {})
        st.session_state[draft_key] = {"rating": current.get("score", None), "comment": current.get("comment", "")}

    draft = st.session_state[draft_key]

    rating_choice = st.radio(
        "Final answer quality (1–5)",
        options=[None, 1, 2, 3, 4, 5],
        index=0 if draft["rating"] is None else [None, 1, 2, 3, 4, 5].index(int(draft["rating"])),
        format_func=lambda x: f"{stars[x]} ({x if x is not None else 'not set'})",
        key=f"rating::{draft_key}",
    )

    comment = st.text_area(
        "Comment (optional)",
        value=draft["comment"],
        key=f"comment::{draft_key}",
        height=120,
    )

    # update draft
    draft["rating"] = rating_choice
    draft["comment"] = comment

    can_submit = rating_choice is not None

    if st.button("Save rating", disabled=not can_submit, use_container_width=True):
        if rating_choice is None:
            st.error("Please select a rating before saving.")
        else:
            try:
                upsert_review_in_traces(
                    traces_path=traces_path,
                    trace_key=trace_id,
                    reviewer_id=reviewer_id,
                    rating=rating_choice,
                    comment=comment,
                )
                st.success("Saved.")
                # Mark as saved in session state instead of deleting/rerunning
                st.session_state[f"{draft_key}::saved"] = True
            except Exception as e:
                st.error(f"Failed to save review: {e}")


if __name__ == "__main__":
    main()
