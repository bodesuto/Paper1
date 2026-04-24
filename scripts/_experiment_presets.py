import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import DATA_PATH, TRAVERSAL_POLICY_PATH
from eval.test.react_test import test as react_test
from eval.test.react_test import test_dual_memory as react_test_dual_memory
from eval.test.reflexion_test import test as reflexion_test
from eval.test.reflexion_test import test_dual_memory as reflexion_test_dual_memory


def run_preset(
    *,
    agent: str,
    mode: str,
    strategy: str | None,
    output_filename: str,
    data_path: str | None = None,
) -> None:
    data_path = data_path or os.path.join(DATA_PATH, "hard_bridge_500_validation.csv")
    output_path = os.path.join(DATA_PATH, output_filename)

    if strategy == "full" and not Path(TRAVERSAL_POLICY_PATH).exists():
        raise FileNotFoundError(
            f"Traversal policy checkpoint not found at {TRAVERSAL_POLICY_PATH}. "
            "Run scripts/run_fit_traversal_policy.py before executing the 'full' preset."
        )

    if agent == "react" and mode == "baseline":
        react_test(data_path, output_path)
        return
    if agent == "react" and mode == "dual_memory":
        react_test_dual_memory(data_path, output_path, retrieval_strategy=strategy or "heuristic")
        return
    if agent == "reflexion" and mode == "baseline":
        reflexion_test(data_path, output_path)
        return
    if agent == "reflexion" and mode == "dual_memory":
        reflexion_test_dual_memory(data_path, output_path, retrieval_strategy=strategy or "heuristic")
        return

    raise ValueError(f"Unsupported preset: agent={agent}, mode={mode}, strategy={strategy}")
