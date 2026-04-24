from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from dotenv import dotenv_values


REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class FieldSpec:
    name: str
    label: str
    field_type: str = "text"
    default: str | int | float | None = None
    help_text: str = ""
    options: list[dict[str, str]] = field(default_factory=list)
    required: bool = False


@dataclass
class RuntimeContext:
    repo_root: Path
    python_executable: str
    env_values: dict[str, str]
    output_path: Path
    data_path: Path

    @property
    def output_stem_path(self) -> Path:
        return self.output_path.with_suffix("")


CommandBuilder = Callable[[dict[str, object], RuntimeContext], list[list[str]]]
OutputBuilder = Callable[[dict[str, object], RuntimeContext], list[str]]


@dataclass
class TaskSpec:
    task_id: str
    title: str
    group: str
    summary: str
    command_builder: CommandBuilder
    fields: list[FieldSpec] = field(default_factory=list)
    expected_outputs: OutputBuilder | None = None
    caution: str = ""
    manual: bool = False
    featured: bool = False


def _load_env_values(repo_root: Path) -> dict[str, str]:
    env_path = repo_root / ".env"
    if not env_path.exists():
        return {}
    values = dotenv_values(env_path)
    return {str(k): str(v) for k, v in values.items() if k and v is not None}


def build_runtime_context(repo_root: Path = REPO_ROOT) -> RuntimeContext:
    env_values = _load_env_values(repo_root)
    output_path = Path(env_values.get("OUTPUT_PATH", "./output/langfuse_export.json"))
    data_path = Path(env_values.get("DATA_PATH", "./eval/data"))
    return RuntimeContext(
        repo_root=repo_root,
        python_executable=sys.executable,
        env_values=env_values,
        output_path=output_path,
        data_path=data_path,
    )


def _py(script: str, *args: str, ctx: RuntimeContext) -> list[str]:
    return [ctx.python_executable, script, *args]


def _value(params: dict[str, object], name: str, fallback: object) -> str:
    raw = params.get(name, fallback)
    return str(raw)


def _int_value(params: dict[str, object], name: str, fallback: int) -> int:
    try:
        return int(params.get(name, fallback))
    except Exception:
        return fallback


def _default_result_filename(agent: str, mode: str, strategy: str) -> str:
    if mode == "baseline":
        return f"{agent}_baseline.csv"
    return f"{agent}_{strategy}.csv"


def _prepare_mini_outputs(params: dict[str, object], ctx: RuntimeContext) -> list[str]:
    size = _int_value(params, "size", 3)
    return [
        str(ctx.data_path / f"mini_train_{size}.csv"),
        str(ctx.data_path / f"mini_validation_{size}.csv"),
    ]


def _smoke_output(default_name: str) -> OutputBuilder:
    def builder(params: dict[str, object], ctx: RuntimeContext) -> list[str]:
        output_path = _value(params, "output_path", default_name)
        return [output_path]

    return builder


def _pipeline_output(suffix: str) -> OutputBuilder:
    def builder(params: dict[str, object], ctx: RuntimeContext) -> list[str]:
        return [str(ctx.output_path.with_suffix(suffix))]

    return builder


def _run_experiment_commands(params: dict[str, object], ctx: RuntimeContext) -> list[list[str]]:
    agent = _value(params, "agent", "react")
    mode = _value(params, "mode", "dual_memory")
    strategy = _value(params, "strategy", "heuristic")
    data_path = _value(params, "data_path", str(ctx.data_path / "hard_bridge_500_validation.csv"))
    output_path = _value(
        params,
        "output_path",
        str(ctx.data_path / _default_result_filename(agent, mode, strategy)),
    )
    return [
        _py(
            "scripts/run_experiment.py",
            "--agent",
            agent,
            "--mode",
            mode,
            "--strategy",
            strategy,
            "--data-path",
            data_path,
            "--output-path",
            output_path,
            ctx=ctx,
        )
    ]


def _run_experiment_outputs(params: dict[str, object], ctx: RuntimeContext) -> list[str]:
    agent = _value(params, "agent", "react")
    mode = _value(params, "mode", "dual_memory")
    strategy = _value(params, "strategy", "heuristic")
    output_path = _value(
        params,
        "output_path",
        str(ctx.data_path / _default_result_filename(agent, mode, strategy)),
    )
    return [output_path]


def _stress_commands(params: dict[str, object], ctx: RuntimeContext) -> list[list[str]]:
    agent = _value(params, "agent", "react")
    strategy = _value(params, "strategy", "full")
    stress = _value(params, "stress", "noisy")
    row_limit = str(_int_value(params, "row_limit", 20))
    data_path = _value(params, "data_path", str(ctx.data_path / "hard_bridge_500_validation.csv"))
    output_path = _value(
        params,
        "output_path",
        str(ctx.data_path / f"{agent}_stress_{stress}.csv"),
    )
    return [
        _py(
            "scripts/run_stress_suite.py",
            "--agent",
            agent,
            "--strategy",
            strategy,
            "--stress",
            stress,
            "--data-path",
            data_path,
            "--output-path",
            output_path,
            "--row-limit",
            row_limit,
            ctx=ctx,
        )
    ]


def _stress_outputs(params: dict[str, object], ctx: RuntimeContext) -> list[str]:
    agent = _value(params, "agent", "react")
    stress = _value(params, "stress", "noisy")
    output_path = _value(
        params,
        "output_path",
        str(ctx.data_path / f"{agent}_stress_{stress}.csv"),
    )
    return [output_path]


def _summary_commands(params: dict[str, object], ctx: RuntimeContext) -> list[list[str]]:
    agent = _value(params, "agent", "react")
    inputs = [
        str(ctx.data_path / "ablations" / f"{agent}_baseline.csv"),
        str(ctx.data_path / "ablations" / f"{agent}_heuristic.csv"),
        str(ctx.data_path / "ablations" / f"{agent}_vector_rag.csv"),
        str(ctx.data_path / "ablations" / f"{agent}_graph_rag.csv"),
        str(ctx.data_path / "ablations" / f"{agent}_ontology_only.csv"),
        str(ctx.data_path / "ablations" / f"{agent}_traversal_only.csv"),
        str(ctx.data_path / "ablations" / f"{agent}_learned.csv"),
        str(ctx.data_path / "ablations" / f"{agent}_full.csv"),
    ]
    output_path = _value(params, "output_path", str(ctx.data_path / f"{agent}_summary.csv"))
    return [_py("scripts/run_result_summary.py", "--inputs", *inputs, "--output-path", output_path, ctx=ctx)]


def _summary_outputs(params: dict[str, object], ctx: RuntimeContext) -> list[str]:
    agent = _value(params, "agent", "react")
    return [_value(params, "output_path", str(ctx.data_path / f"{agent}_summary.csv"))]


def _transfer_commands(params: dict[str, object], ctx: RuntimeContext) -> list[list[str]]:
    agent = _value(params, "agent", "react")
    in_domain = _value(params, "in_domain", str(ctx.data_path / "ablations" / f"{agent}_full.csv"))
    out_domain = _value(params, "out_domain", str(ctx.data_path / f"{agent}_otherdomain.csv"))
    output_path = _value(params, "output_path", str(ctx.data_path / f"{agent}_transfer_summary.csv"))
    return [
        _py(
            "scripts/run_transfer_eval.py",
            "--in-domain",
            in_domain,
            "--out-of-domain",
            out_domain,
            "--output-path",
            output_path,
            ctx=ctx,
        )
    ]


def _transfer_outputs(params: dict[str, object], ctx: RuntimeContext) -> list[str]:
    agent = _value(params, "agent", "react")
    return [_value(params, "output_path", str(ctx.data_path / f"{agent}_transfer_summary.csv"))]


def _learned_stack_commands(params: dict[str, object], ctx: RuntimeContext) -> list[list[str]]:
    return [
        _py("scripts/run_insert_obs.py", ctx=ctx),
        _py("scripts/run_build_ontology_dataset.py", ctx=ctx),
        _py("scripts/run_fit_ontology_prototypes.py", ctx=ctx),
        _py("scripts/run_insert_obs.py", ctx=ctx),
        _py("scripts/run_react_learned.py", ctx=ctx),
        _py("scripts/run_build_policy_dataset.py", "--input-path", "./eval/data/react_learned.csv", ctx=ctx),
        _py("scripts/run_fit_traversal_policy.py", ctx=ctx),
    ]


def _learned_stack_outputs(params: dict[str, object], ctx: RuntimeContext) -> list[str]:
    return [
        str(ctx.output_path.with_suffix(".ontology_dataset.json")),
        str(ctx.output_path.with_suffix(".ontology_prototypes.json")),
        str(ctx.data_path / "react_learned.csv"),
        str(ctx.output_path.with_suffix(".traversal_policy_dataset.json")),
        str(ctx.output_path.with_suffix(".traversal_policy.json")),
    ]


def _paper_bundle_commands(agent: str) -> CommandBuilder:
    def builder(params: dict[str, object], ctx: RuntimeContext) -> list[list[str]]:
        commands = [
            _py("scripts/run_experiment.py", "--agent", agent, "--mode", "dual_memory", "--strategy", "full", "--output-path", f"./eval/data/{agent}_full.csv", ctx=ctx),
            _py("scripts/run_ablation_suite.py", "--agent", agent, ctx=ctx),
        ]
        if agent == "react":
            commands.append(
                _py(
                    "scripts/run_stress_suite.py",
                    "--agent",
                    "react",
                    "--strategy",
                    "full",
                    "--stress",
                    "noisy",
                    "--output-path",
                    "./eval/data/react_stress_noisy.csv",
                    ctx=ctx,
                )
            )
        commands.append(
            _py(
                "scripts/run_result_summary.py",
                "--inputs",
                f"./eval/data/ablations/{agent}_baseline.csv",
                f"./eval/data/ablations/{agent}_heuristic.csv",
                f"./eval/data/ablations/{agent}_vector_rag.csv",
                f"./eval/data/ablations/{agent}_graph_rag.csv",
                f"./eval/data/ablations/{agent}_ontology_only.csv",
                f"./eval/data/ablations/{agent}_traversal_only.csv",
                f"./eval/data/ablations/{agent}_learned.csv",
                f"./eval/data/ablations/{agent}_full.csv",
                "--output-path",
                f"./eval/data/{agent}_summary.csv",
                ctx=ctx,
            )
        )
        return commands

    return builder


def _paper_bundle_outputs(agent: str) -> OutputBuilder:
    def builder(params: dict[str, object], ctx: RuntimeContext) -> list[str]:
        outputs = [
            str(ctx.data_path / f"{agent}_full.csv"),
            str(ctx.data_path / "ablations"),
            str(ctx.data_path / f"{agent}_summary.csv"),
        ]
        if agent == "react":
            outputs.append(str(ctx.data_path / "react_stress_noisy.csv"))
        return outputs

    return builder


def get_task_specs(ctx: RuntimeContext) -> list[TaskSpec]:
    return [
        TaskSpec(
            task_id="test_llm",
            title="Test LLM",
            group="Quick Checks",
            summary="Kiểm tra Gemini và env hoạt động bình thường.",
            command_builder=lambda params, ctx: [_py("scripts/run_test_llm.py", ctx=ctx)],
            expected_outputs=lambda params, ctx: [],
            featured=True,
        ),
        TaskSpec(
            task_id="prepare_mini_data",
            title="Prepare Mini Data",
            group="Quick Checks",
            summary="Tạo mini train/validation hoặc tự bootstrap HotpotQA nếu còn thiếu.",
            command_builder=lambda params, ctx: [
                _py("scripts/run_prepare_mini_data.py", "--size", str(_int_value(params, "size", 3)), ctx=ctx)
            ],
            fields=[FieldSpec("size", "Rows per split", "number", 3, required=True)],
            expected_outputs=_prepare_mini_outputs,
        ),
        TaskSpec(
            task_id="react_smoke",
            title="ReAct Smoke",
            group="Quick Checks",
            summary="Chạy nhanh ReAct trên mini data, không cần Neo4j.",
            command_builder=lambda params, ctx: [
                _py(
                    "scripts/run_react_smoke.py",
                    "--data-path",
                    _value(params, "data_path", "./eval/data/mini_validation_3.csv"),
                    "--limit",
                    str(_int_value(params, "limit", 1)),
                    "--output-path",
                    _value(params, "output_path", "./eval/data/react_smoke_results.csv"),
                    ctx=ctx,
                )
            ],
            fields=[
                FieldSpec("data_path", "Data path", "text", "./eval/data/mini_validation_3.csv"),
                FieldSpec("limit", "Rows to run", "number", 1),
                FieldSpec("output_path", "Output CSV", "text", "./eval/data/react_smoke_results.csv"),
            ],
            expected_outputs=_smoke_output("./eval/data/react_smoke_results.csv"),
        ),
        TaskSpec(
            task_id="reflexion_smoke",
            title="Reflexion Smoke",
            group="Quick Checks",
            summary="Chạy nhanh Reflexion trên mini data, không cần Neo4j.",
            command_builder=lambda params, ctx: [
                _py(
                    "scripts/run_reflexion_smoke.py",
                    "--data-path",
                    _value(params, "data_path", "./eval/data/mini_validation_3.csv"),
                    "--limit",
                    str(_int_value(params, "limit", 1)),
                    "--output-path",
                    _value(params, "output_path", "./eval/data/reflexion_smoke_results.csv"),
                    ctx=ctx,
                )
            ],
            fields=[
                FieldSpec("data_path", "Data path", "text", "./eval/data/mini_validation_3.csv"),
                FieldSpec("limit", "Rows to run", "number", 1),
                FieldSpec("output_path", "Output CSV", "text", "./eval/data/reflexion_smoke_results.csv"),
            ],
            expected_outputs=_smoke_output("./eval/data/reflexion_smoke_results.csv"),
        ),
        TaskSpec(
            task_id="smoke_bundle",
            title="Smoke Bundle",
            group="Quick Checks",
            summary="Chuỗi thao tác ngắn nhất để xác nhận app chạy được: mini data + ReAct smoke + Reflexion smoke.",
            command_builder=lambda params, ctx: [
                _py("scripts/run_prepare_mini_data.py", "--size", str(_int_value(params, "size", 3)), ctx=ctx),
                _py("scripts/run_react_smoke.py", "--limit", str(_int_value(params, "react_limit", 1)), ctx=ctx),
                _py("scripts/run_reflexion_smoke.py", "--limit", str(_int_value(params, "reflexion_limit", 1)), ctx=ctx),
            ],
            fields=[
                FieldSpec("size", "Mini rows", "number", 3),
                FieldSpec("react_limit", "ReAct rows", "number", 1),
                FieldSpec("reflexion_limit", "Reflexion rows", "number", 1),
            ],
            expected_outputs=lambda params, ctx: [
                str(ctx.data_path / "react_smoke_results.csv"),
                str(ctx.data_path / "reflexion_smoke_results.csv"),
            ],
            featured=True,
        ),
        TaskSpec(
            task_id="export_runs",
            title="Export Langfuse Traces",
            group="Full Pipeline",
            summary="Xuat trace tu Langfuse sang JSON output cua repo.",
            command_builder=lambda params, ctx: [_py("scripts/run_export.py", ctx=ctx)],
            expected_outputs=lambda params, ctx: [str(ctx.output_path)],
        ),
        TaskSpec(
            task_id="format_trace",
            title="Format Trace",
            group="Full Pipeline",
            summary="Chuyển JSON export sang định dạng ReAct trace text.",
            command_builder=lambda params, ctx: [_py("scripts/run_format_trace.py", ctx=ctx)],
            expected_outputs=_pipeline_output(".react.txt"),
        ),
        TaskSpec(
            task_id="run_rca",
            title="Run RCA",
            group="Full Pipeline",
            summary="Chạy root cause analysis trên trace đã chuẩn hóa.",
            command_builder=lambda params, ctx: [_py("scripts/run_rca.py", ctx=ctx)],
            expected_outputs=_pipeline_output(".rca.json"),
        ),
        TaskSpec(
            task_id="run_kbv",
            title="Run KBV",
            group="Full Pipeline",
            summary="Chạy knowledge-based verification / DeepEval.",
            command_builder=lambda params, ctx: [_py("scripts/run_kbv.py", ctx=ctx)],
            expected_outputs=_pipeline_output(".kbv.json"),
            caution="Bước này tốn API quota hơn smoke test.",
        ),
        TaskSpec(
            task_id="run_hil",
            title="Open HIL Review",
            group="Full Pipeline",
            summary="Mở Streamlit để review traces bằng người dùng.",
            command_builder=lambda params, ctx: [_py("scripts/run_hil_streamlit.py", ctx=ctx)],
            expected_outputs=_pipeline_output(".hil.json"),
            manual=True,
            caution="Lệnh này mở Streamlit và chạy tương tác, không phải batch job tự hoàn tất ngay.",
        ),
        TaskSpec(
            task_id="run_classify",
            title="Classify Memory",
            group="Full Pipeline",
            summary="Sinh classified traces và classified insights.",
            command_builder=lambda params, ctx: [_py("scripts/run_classify.py", ctx=ctx)],
            expected_outputs=lambda params, ctx: [
                str(ctx.output_path.with_suffix(".classified.json")),
                str(ctx.output_path.with_suffix(".classified_insights.json")),
            ],
        ),
        TaskSpec(
            task_id="insert_obs",
            title="Insert Neo4j",
            group="Full Pipeline",
            summary="Insert classified payloads vào dual-memory graph trên Neo4j.",
            command_builder=lambda params, ctx: [_py("scripts/run_insert_obs.py", ctx=ctx)],
            expected_outputs=lambda params, ctx: [],
            caution="Cần Neo4j chạy sẵn và credentials hợp lệ trong .env.",
        ),
        TaskSpec(
            task_id="build_ontology_dataset",
            title="Build Ontology Dataset",
            group="Learning",
            summary="Tạo dataset huấn luyện ontology từ classified artifacts.",
            command_builder=lambda params, ctx: [_py("scripts/run_build_ontology_dataset.py", ctx=ctx)],
            expected_outputs=_pipeline_output(".ontology_dataset.json"),
        ),
        TaskSpec(
            task_id="fit_ontology",
            title="Fit Ontology Prototypes",
            group="Learning",
            summary="Huấn luyện adaptive ontology prototypes.",
            command_builder=lambda params, ctx: [_py("scripts/run_fit_ontology_prototypes.py", ctx=ctx)],
            expected_outputs=_pipeline_output(".ontology_prototypes.json"),
        ),
        TaskSpec(
            task_id="graph_bootstrap_bundle",
            title="Graph Bootstrap Bundle",
            group="Learning",
            summary="Chuỗi khởi tạo graph học được: insert -> ontology dataset -> fit ontology -> insert lại.",
            command_builder=lambda params, ctx: [
                _py("scripts/run_insert_obs.py", ctx=ctx),
                _py("scripts/run_build_ontology_dataset.py", ctx=ctx),
                _py("scripts/run_fit_ontology_prototypes.py", ctx=ctx),
                _py("scripts/run_insert_obs.py", ctx=ctx),
            ],
            expected_outputs=lambda params, ctx: [
                str(ctx.output_path.with_suffix(".ontology_dataset.json")),
                str(ctx.output_path.with_suffix(".ontology_prototypes.json")),
            ],
            caution="Cần classified outputs và Neo4j sẵn sàng.",
            featured=True,
        ),
        TaskSpec(
            task_id="build_policy_dataset",
            title="Build Traversal Dataset",
            group="Learning",
            summary="Chuyển retrieval logs thành episodes cho traversal learner.",
            command_builder=lambda params, ctx: [
                _py(
                    "scripts/run_build_policy_dataset.py",
                    "--input-path",
                    _value(params, "input_path", "./eval/data/react_learned.csv"),
                    "--output-path",
                    _value(params, "output_path", str(ctx.output_path.with_suffix(".traversal_policy_dataset.json"))),
                    ctx=ctx,
                )
            ],
            fields=[
                FieldSpec("input_path", "Input retrieval CSV", "text", "./eval/data/react_learned.csv"),
                FieldSpec(
                    "output_path",
                    "Output JSON",
                    "text",
                    str(build_runtime_context().output_path.with_suffix(".traversal_policy_dataset.json")),
                ),
            ],
            expected_outputs=lambda params, ctx: [
                _value(params, "output_path", str(ctx.output_path.with_suffix(".traversal_policy_dataset.json")))
            ],
        ),
        TaskSpec(
            task_id="fit_traversal_policy",
            title="Fit Traversal Policy",
            group="Learning",
            summary="Huấn luyện learned traversal ranking policy.",
            command_builder=lambda params, ctx: [
                _py(
                    "scripts/run_fit_traversal_policy.py",
                    "--input-path",
                    _value(params, "input_path", str(ctx.output_path.with_suffix(".traversal_policy_dataset.json"))),
                    "--output-path",
                    _value(params, "output_path", str(ctx.output_path.with_suffix(".traversal_policy.json"))),
                    ctx=ctx,
                )
            ],
            fields=[
                FieldSpec(
                    "input_path",
                    "Policy dataset",
                    "text",
                    str(build_runtime_context().output_path.with_suffix(".traversal_policy_dataset.json")),
                ),
                FieldSpec(
                    "output_path",
                    "Policy checkpoint",
                    "text",
                    str(build_runtime_context().output_path.with_suffix(".traversal_policy.json")),
                ),
            ],
            expected_outputs=lambda params, ctx: [
                _value(params, "output_path", str(ctx.output_path.with_suffix(".traversal_policy.json")))
            ],
        ),
        TaskSpec(
            task_id="traversal_bootstrap_bundle",
            title="Traversal Bootstrap Bundle",
            group="Learning",
            summary="Khởi tạo learned retrieval + policy dataset + traversal policy trong một lần chạy.",
            command_builder=lambda params, ctx: [
                _py("scripts/run_react_learned.py", ctx=ctx),
                _py("scripts/run_build_policy_dataset.py", "--input-path", "./eval/data/react_learned.csv", ctx=ctx),
                _py("scripts/run_fit_traversal_policy.py", ctx=ctx),
            ],
            expected_outputs=lambda params, ctx: [
                str(ctx.data_path / "react_learned.csv"),
                str(ctx.output_path.with_suffix(".traversal_policy_dataset.json")),
                str(ctx.output_path.with_suffix(".traversal_policy.json")),
            ],
            featured=True,
        ),
        TaskSpec(
            task_id="learned_stack_bundle",
            title="Learned Stack Bundle",
            group="Learning",
            summary="Chuỗi hoàn chỉnh để dựng ontology + traversal learned stack cho repo hiện tại.",
            command_builder=_learned_stack_commands,
            expected_outputs=_learned_stack_outputs,
            caution="Cần classified outputs, Neo4j sẵn sàng, và learned retrieval sẽ tốn thời gian hơn smoke test.",
            featured=True,
        ),
        TaskSpec(
            task_id="run_experiment",
            title="Run Experiment",
            group="Experiments",
            summary="Runner tổng quát cho baseline hoặc dual-memory strategy.",
            command_builder=_run_experiment_commands,
            fields=[
                FieldSpec(
                    "agent",
                    "Agent",
                    "select",
                    "react",
                    options=[{"label": "ReAct", "value": "react"}, {"label": "Reflexion", "value": "reflexion"}],
                ),
                FieldSpec(
                    "mode",
                    "Mode",
                    "select",
                    "dual_memory",
                    options=[{"label": "Baseline", "value": "baseline"}, {"label": "Dual Memory", "value": "dual_memory"}],
                ),
                FieldSpec(
                    "strategy",
                    "Strategy",
                    "select",
                    "heuristic",
                    options=[
                        {"label": "heuristic", "value": "heuristic"},
                        {"label": "vector_rag", "value": "vector_rag"},
                        {"label": "graph_rag", "value": "graph_rag"},
                        {"label": "ontology_only", "value": "ontology_only"},
                        {"label": "traversal_only", "value": "traversal_only"},
                        {"label": "learned", "value": "learned"},
                        {"label": "full", "value": "full"},
                    ],
                ),
                FieldSpec("data_path", "Data path", "text", "./eval/data/hard_bridge_500_validation.csv"),
                FieldSpec("output_path", "Output CSV", "text", ""),
            ],
            expected_outputs=_run_experiment_outputs,
            caution="`full` chỉ chạy ổn khi đã có traversal policy checkpoint.",
            featured=True,
        ),
        TaskSpec(
            task_id="run_ablation_suite",
            title="Run Ablation Suite",
            group="Experiments",
            summary="Chạy compact ablation suite cho react hoặc reflexion.",
            command_builder=lambda params, ctx: [
                _py(
                    "scripts/run_ablation_suite.py",
                    "--agent",
                    _value(params, "agent", "react"),
                    "--data-path",
                    _value(params, "data_path", str(ctx.data_path / "hard_bridge_500_validation.csv")),
                    "--output-dir",
                    _value(params, "output_dir", str(ctx.data_path / "ablations")),
                    ctx=ctx,
                )
            ],
            fields=[
                FieldSpec(
                    "agent",
                    "Agent",
                    "select",
                    "react",
                    options=[{"label": "ReAct", "value": "react"}, {"label": "Reflexion", "value": "reflexion"}],
                ),
                FieldSpec("data_path", "Data path", "text", "./eval/data/hard_bridge_500_validation.csv"),
                FieldSpec("output_dir", "Output directory", "text", "./eval/data/ablations"),
            ],
            expected_outputs=lambda params, ctx: [_value(params, "output_dir", "./eval/data/ablations")],
        ),
        TaskSpec(
            task_id="run_stress_suite",
            title="Run Stress Suite",
            group="Experiments",
            summary="Chạy noisy/missing/contradictory stress test cho memory-grounded reasoning.",
            command_builder=_stress_commands,
            fields=[
                FieldSpec(
                    "agent",
                    "Agent",
                    "select",
                    "react",
                    options=[{"label": "ReAct", "value": "react"}, {"label": "Reflexion", "value": "reflexion"}],
                ),
                FieldSpec(
                    "strategy",
                    "Strategy",
                    "select",
                    "full",
                    options=[
                        {"label": "heuristic", "value": "heuristic"},
                        {"label": "ontology_only", "value": "ontology_only"},
                        {"label": "traversal_only", "value": "traversal_only"},
                        {"label": "learned", "value": "learned"},
                        {"label": "full", "value": "full"},
                    ],
                ),
                FieldSpec(
                    "stress",
                    "Stress type",
                    "select",
                    "noisy",
                    options=[
                        {"label": "noisy", "value": "noisy"},
                        {"label": "missing", "value": "missing"},
                        {"label": "contradictory", "value": "contradictory"},
                    ],
                ),
                FieldSpec("row_limit", "Row limit", "number", 20),
                FieldSpec("data_path", "Data path", "text", "./eval/data/hard_bridge_500_validation.csv"),
                FieldSpec("output_path", "Output CSV", "text", ""),
            ],
            expected_outputs=_stress_outputs,
        ),
        TaskSpec(
            task_id="run_result_summary",
            title="Summarize Results",
            group="Experiments",
            summary="Gộp các file ablation thành một summary CSV phục vụ paper/table.",
            command_builder=_summary_commands,
            fields=[
                FieldSpec(
                    "agent",
                    "Agent family",
                    "select",
                    "react",
                    options=[{"label": "react", "value": "react"}, {"label": "reflexion", "value": "reflexion"}],
                ),
                FieldSpec("output_path", "Output CSV", "text", ""),
            ],
            expected_outputs=_summary_outputs,
        ),
        TaskSpec(
            task_id="run_transfer_eval",
            title="Transfer Summary",
            group="Experiments",
            summary="So sánh in-domain và out-of-domain runs.",
            command_builder=_transfer_commands,
            fields=[
                FieldSpec(
                    "agent",
                    "Agent family",
                    "select",
                    "react",
                    options=[{"label": "react", "value": "react"}, {"label": "reflexion", "value": "reflexion"}],
                ),
                FieldSpec("in_domain", "In-domain CSV", "text", ""),
                FieldSpec("out_domain", "Out-of-domain CSV", "text", ""),
                FieldSpec("output_path", "Output CSV", "text", ""),
            ],
            expected_outputs=_transfer_outputs,
        ),
        TaskSpec(
            task_id="react_paper_bundle",
            title="ReAct Paper Bundle",
            group="Experiments",
            summary="Chạy ReAct full + ablation + noisy stress + summary theo một preset lớn.",
            command_builder=_paper_bundle_commands("react"),
            expected_outputs=_paper_bundle_outputs("react"),
            caution="Preset này dài và tốn quota. Chỉ chạy sau khi ontology và traversal policy đã sẵn sàng.",
            featured=True,
        ),
        TaskSpec(
            task_id="reflexion_paper_bundle",
            title="Reflexion Paper Bundle",
            group="Experiments",
            summary="Chạy Reflexion full + ablation + summary theo một preset lớn.",
            command_builder=_paper_bundle_commands("reflexion"),
            expected_outputs=_paper_bundle_outputs("reflexion"),
            caution="Preset này dài và tốn quota. Chỉ chạy sau khi ontology và traversal policy đã sẵn sàng.",
            featured=True,
        ),
    ]
