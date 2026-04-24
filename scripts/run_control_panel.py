import argparse
import sys
from pathlib import Path

import uvicorn


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def main():
    parser = argparse.ArgumentParser(description="Run the local DualMemoryKG control panel.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    uvicorn.run(
        "control_panel.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        reload_dirs=[str(REPO_ROOT)] if args.reload else None,
    )


if __name__ == "__main__":
    main()
