import sys
from pathlib import Path

# Add parent directory to path so we can import common
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.models import get_llm

if __name__ == "__main__":
    llm = get_llm()
    resp = llm.invoke("Say hello in one short sentence.")
    print(resp.content)
