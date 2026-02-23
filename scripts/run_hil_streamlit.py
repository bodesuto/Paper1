from pathlib import Path
import json
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from common.config import OUTPUT_PATH

TRACE_JSON = Path(OUTPUT_PATH).with_suffix(".kbv.json")
reviews_path = Path(OUTPUT_PATH).with_suffix(".hil.json")

# Initialize .hil.json if it doesn't exist
if not reviews_path.exists():
    if TRACE_JSON.exists():
        with TRACE_JSON.open("r", encoding="utf-8") as f:
            traces = json.load(f)
        # Filter to only non-hallucinated traces
        non_hallucinated = [t for t in traces if not t.get("hallucinated", True)]
        print(f"Found {len(non_hallucinated)} non-hallucinated traces out of {len(traces)}")
        
        # Copy non-hallucinated traces to reviews file
        reviews_path.parent.mkdir(parents=True, exist_ok=True)
        with reviews_path.open("w", encoding="utf-8") as f:
            json.dump(non_hallucinated, f, indent=2, ensure_ascii=False)
        print(f"✓ Initialized {reviews_path} with {len(non_hallucinated)} non-hallucinated traces")
    else:
        print(f"Error: {TRACE_JSON} not found")
        sys.exit(1)

# Run the streamlit app
app_path = Path(__file__).parent.parent / "diagnostics" / "hil" / "src" / "app.py"
subprocess.run(["streamlit", "run", str(app_path)])
