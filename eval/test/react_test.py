from pathlib import Path
import json
import time

from neo4j import GraphDatabase
import pandas as pd
from agents.src.react import create_react_agent, format_examples, get_tool_calls, clear_tool_calls
from common.config import RETRIEVAL_STRATEGY
from common.env_setup import apply_env
from common.models import get_llm_with_trace
from agents.prompts.hotpot_examples import react_examples
from eval.test.grounding_metrics import summarize_grounding_metrics
from eval.test.matrics import (
    build_test_case,
    safe_measure,
    is_bad_call,
    exact_match_metric,
    answer_relevancy_metric,
    faithfulness_metric,
    ctx_precision_metric,
    build_instruction_inconsistency_metric,
    build_context_inconsistency_metric,
    build_logical_inconsistency_metric,
)

from eval.test.utils import FullReActTrace, get_database_session, get_usage_callback
from knowledge_graph.src.retrieve_data import retrieve_memory_bundle
from knowledge_graph.src.retrieve_heuristic import bundle_to_prompt_payload


def train(data_path: str | Path):
    apply_env()
    df_bridge = pd.read_csv(data_path)
    print(f"Loaded data from {data_path} (length: {len(df_bridge)})")

     # Replace with actual trace handler if available
    agent = create_react_agent()  # Pass None or a trace handler if

    for _, row in df_bridge.iterrows():
        question = row["question"]
        expected = row.get("answer")
        try:
            actual = agent.invoke({"input": question, "examples": format_examples(react_examples)})
        except Exception as e:
            actual = f"ERROR: {e}"
        if isinstance(actual, dict):
            actual_text = actual.get("output", str(actual))
        else:
            actual_text = str(actual)
        print(f"Question: {question} | Expected: {expected} | Actual: {actual_text}")

def test(data_path: str | Path, output_path: str | Path):
    apply_env()
    df_bridge = pd.read_csv(data_path)
    print(f"Loaded data from {data_path} (length: {len(df_bridge)})")

    trace_handler = FullReActTrace() 
    agent = create_react_agent(llm=get_llm_with_trace(trace_handler))  # Pass trace handler to get_llm_with_trace

    results = []
    total = 0
    success = 0
    exact_match_success = 0
    SAVE_PATH = Path(output_path)
    
    for i, row in df_bridge.iterrows():
        # Clear thread-local tool_calls before each run
        clear_tool_calls()
        expected_output = row["answer"]
        question = row["question"]
        with get_usage_callback() as cb:
            agent_start = time.perf_counter()
            actual_answer = agent.invoke({"input": question, "examples": format_examples(react_examples)})
            # Extract output if it's a dict
            if isinstance(actual_answer, dict):
                actual_answer = actual_answer.get("output", str(actual_answer))
            agent_end = time.perf_counter()
            print(f"[{i}] Agent took {agent_end - agent_start:.4f} seconds")

            trace_text = trace_handler.trace.split("Begin!\n", 1)[1] if "Begin!\n" in trace_handler.trace else trace_handler.trace
            
            is_exact = expected_output in actual_answer
            success += int(is_exact)
            total += 1

            current_tool_calls = get_tool_calls()
            bad_calls = [c for c in current_tool_calls if is_bad_call(c)]

            # Build test case for all metrics
            test_case = build_test_case(
                question=question,
                gold_answer=expected_output,
                actual_answer=actual_answer,
                tool_calls=current_tool_calls,
                trace_text=trace_text,
            )

            # Evaluate exact match using DeepEval
            exact_match_score = safe_measure(exact_match_metric, test_case)
            exact_match_success += int(exact_match_score.score)

            answer_rel_score = safe_measure(answer_relevancy_metric, test_case)
            faithfulness_score = safe_measure(faithfulness_metric, test_case)
            ctx_precision_score = safe_measure(ctx_precision_metric, test_case)
            instruction_inconsistency_score = safe_measure(build_instruction_inconsistency_metric, test_case)
            context_inconsistency_score = safe_measure(build_context_inconsistency_metric, test_case)
            logical_inconsistency_score = safe_measure(build_logical_inconsistency_metric, test_case)

            results.append({
                "index": row.get("id", i),
                "question": question,
                "gold_answer": expected_output,
                "actual_answer": actual_answer,
                "exact_match": is_exact,
                "exact_match_eval": exact_match_score.score,
                "exact_match_eval_success": exact_match_score.success,
                "bad_calls": len(bad_calls),
                "total_calls": len(current_tool_calls),
                "agent_latency_s": agent_end - agent_start,
                # Token usage
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_tokens": cb.total_tokens,
                # LLM calls
                "llm_calls": cb.successful_requests,
                # Cost
                "cost_usd": cb.total_cost,
                "answer_relevancy_score": answer_rel_score.score,
                "answer_relevancy_reason": answer_rel_score.reason,
                "faithfulness_score": faithfulness_score.score,
                "faithfulness_reason": faithfulness_score.reason,
                "ctx_precision_score": ctx_precision_score.score,
                "ctx_precision_reason": ctx_precision_score.reason,
                "instruction_inconsistency_score": instruction_inconsistency_score.score,
                "instruction_inconsistency_reason": instruction_inconsistency_score.reason,
                "context_inconsistency_score": context_inconsistency_score.score,
                "context_inconsistency_reason": context_inconsistency_score.reason,
                "logical_inconsistency_score": logical_inconsistency_score.score,
                "logical_inconsistency_reason": logical_inconsistency_score.reason,
            })
            df_results = pd.DataFrame(results)
            df_results.to_csv(SAVE_PATH, index=False)

    print("\n===== FINAL SUMMARY =====")
    print("Total:", total)
    print("Exact Match (substring):", success)
    print("Exact Match (evaluated):", exact_match_success)
    print(f"Saved CSV: {SAVE_PATH}")

def test_dual_memory(
    data_path: str | Path,
    output_path: str | Path,
    retrieval_strategy: str = RETRIEVAL_STRATEGY,
    memory_transform=None,
    row_limit: int | None = None,
):
    apply_env()
    df_bridge = pd.read_csv(data_path)
    print(f"Loaded data from {data_path} (length: {len(df_bridge)})")

    trace_handler = FullReActTrace() 
    agent = create_react_agent(llm=get_llm_with_trace(trace_handler))  # Pass trace handler to get_llm_with_trace

    results = []
    total = 0
    success = 0
    exact_match_success = 0
    SAVE_PATH = Path(output_path)
    with get_database_session() as session:
        iterator = df_bridge.iterrows() if row_limit is None else df_bridge.head(row_limit).iterrows()
        for i, row in iterator:
            # Clear thread-local tool_calls before each run
            clear_tool_calls()
            expected_output = row["answer"]
            question = row["question"]
            mem_start = time.perf_counter()
            memory_bundle = retrieve_memory_bundle(question, session=session, strategy=retrieval_strategy)
            experience_examples = bundle_to_prompt_payload(memory_bundle, fallback_examples=react_examples)
            if memory_transform is not None:
                experience_examples = memory_transform(experience_examples, row=row.to_dict())
            mem_end = time.perf_counter()
            selected_path = memory_bundle.selected_path_summary()
            candidate_path = memory_bundle.path_summary()
            with get_usage_callback() as cb:
                agent_start = time.perf_counter()
                actual_answer = agent.invoke({"input": question, "examples": format_examples(experience_examples)})
                # Extract output if it's a dict
                if isinstance(actual_answer, dict):
                    actual_answer = actual_answer.get("output", str(actual_answer))
                agent_end = time.perf_counter()
                print(f"[{i}] Agent took {agent_end - agent_start:.4f} seconds")

                trace_text = trace_handler.trace.split("Begin!\n", 1)[1] if "Begin!\n" in trace_handler.trace else trace_handler.trace
                
                is_exact = expected_output in actual_answer
                success += int(is_exact)
                total += 1

                current_tool_calls = get_tool_calls()
                bad_calls = [c for c in current_tool_calls if is_bad_call(c)]

                # Build test case for all metrics
                test_case = build_test_case(
                    question=question,
                    gold_answer=expected_output,
                    actual_answer=actual_answer,
                    tool_calls=current_tool_calls,
                    trace_text=trace_text,
                    retrieval_path=selected_path,
                    memory_payload=experience_examples,
                    retrieval_strategy=memory_bundle.strategy,
                )

                # Evaluate exact match using DeepEval
                exact_match_score = safe_measure(exact_match_metric, test_case)
                exact_match_success += int(exact_match_score.score)

                answer_rel_score = safe_measure(answer_relevancy_metric, test_case)
                faithfulness_score = safe_measure(faithfulness_metric, test_case)
                ctx_precision_score = safe_measure(ctx_precision_metric, test_case)
                instruction_inconsistency_score = safe_measure(build_instruction_inconsistency_metric, test_case)
                context_inconsistency_score = safe_measure(build_context_inconsistency_metric, test_case)
                logical_inconsistency_score = safe_measure(build_logical_inconsistency_metric, test_case)
                grounding_scores = summarize_grounding_metrics(
                    question=question,
                    answer=actual_answer,
                    retrieval_path=selected_path,
                    memory_payload=experience_examples,
                    tool_calls=current_tool_calls,
                )

                results.append({
                    "index": row.get("id", i),
                    "question": question,
                    "gold_answer": expected_output,
                    "actual_answer": actual_answer,
                    "exact_match": is_exact,
                    "exact_match_eval": exact_match_score.score,
                    "exact_match_eval_success": exact_match_score.success,
                    "bad_calls": len(bad_calls),
                    "total_calls": len(current_tool_calls),
                    # Latencies
                    "memory_latency_s": mem_end - mem_start,
                    "agent_latency_s": agent_end - agent_start,
                    "total_latency_s": (mem_end - mem_start) + (agent_end - agent_start),
                    "retrieval_strategy": memory_bundle.strategy,
                    "retrieved_node_ids": json.dumps(memory_bundle.selected_node_ids(), ensure_ascii=False),
                    "retrieved_memory_types": json.dumps(memory_bundle.selected_memory_types(), ensure_ascii=False),
                    "retrieval_path": json.dumps(selected_path, ensure_ascii=False),
                    "candidate_node_ids": json.dumps([node.node_id for node in memory_bundle.nodes if node.node_id], ensure_ascii=False),
                    "candidate_memory_types": json.dumps(memory_bundle.memory_types(), ensure_ascii=False),
                    "candidate_retrieval_path": json.dumps(candidate_path, ensure_ascii=False),
                    "memory_payload": json.dumps(experience_examples, ensure_ascii=False),
                    "traversal": json.dumps(memory_bundle.metadata.get("traversal", {}), ensure_ascii=False),
                    # Token usage
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "total_tokens": cb.total_tokens,
                    # LLM calls
                    "llm_calls": cb.successful_requests,
                    # Cost
                    "cost_usd": cb.total_cost,
                    "answer_relevancy_score": answer_rel_score.score,
                    "answer_relevancy_reason": answer_rel_score.reason,
                    "faithfulness_score": faithfulness_score.score,
                    "faithfulness_reason": faithfulness_score.reason,
                    "ctx_precision_score": ctx_precision_score.score,
                    "ctx_precision_reason": ctx_precision_score.reason,
                    "instruction_inconsistency_score": instruction_inconsistency_score.score,
                    "instruction_inconsistency_reason": instruction_inconsistency_score.reason,
                    "context_inconsistency_score": context_inconsistency_score.score,
                    "context_inconsistency_reason": context_inconsistency_score.reason,
                    "logical_inconsistency_score": logical_inconsistency_score.score,
                    "logical_inconsistency_reason": logical_inconsistency_score.reason,
                    "lexical_support_ratio": grounding_scores["lexical_support_ratio"],
                    "unsupported_reasoning_score": grounding_scores["unsupported_reasoning_score"],
                    "path_grounding_precision": grounding_scores["path_grounding_precision"],
                    "memory_selection_accuracy": grounding_scores["memory_selection_accuracy"],
                    "evidence_sufficiency_rate": grounding_scores["evidence_sufficiency_rate"],
                })
                df_results = pd.DataFrame(results)
                df_results.to_csv(SAVE_PATH, index=False)

    print("\n===== FINAL SUMMARY =====")
    print("Total:", total)
    print("Exact Match (substring):", success)
    print("Exact Match (evaluated):", exact_match_success)
    print(f"Saved CSV: {SAVE_PATH}")
