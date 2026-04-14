from pathlib import Path
import json
import time

from neo4j import GraphDatabase
import pandas as pd
from agents.src.react import creat_react_agent, format_examples, tool_calls
from common.env_setup import apply_env
from common.models import get_llm_with_trace
from agents.prompts.hotpot_examples import react_examples
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
from knowledge_graph.src.retrieve_data import retrieve_memories


def train(data_path: str | Path):
    apply_env()
    df_bridge = pd.read_csv(data_path)
    print(f"Loaded data from {data_path} (length: {len(df_bridge)})")

     # Replace with actual trace handler if available
    agent = creat_react_agent()  # Pass None or a trace handler if

    for _, row in df_bridge.iterrows():
        question = row["question"]
        expected = row.get("answer")
        try:
            actual = agent.invoke({"input": question, "examples": format_examples(react_examples)})
        except Exception as e:
            actual = f"ERROR: {e}"
        print(f"Question: {question} | Expected: {expected} | Actual: {actual['output']}")

def test(data_path: str | Path, output_path: str | Path):
    apply_env()
    df_bridge = pd.read_csv(data_path)
    print(f"Loaded data from {data_path} (length: {len(df_bridge)})")

    trace_handler = FullReActTrace() 
    agent = creat_react_agent(llm=get_llm_with_trace(trace_handler))  # Pass trace handler to get_llm_with_trace

    results = []
    total = 0
    success = 0
    exact_match_success = 0
    SAVE_PATH = Path(output_path)
    
    for i, row in df_bridge.iterrows():
        # Clear global tool_calls before each run
        tool_calls.clear()
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

            bad_calls = [c for c in tool_calls if is_bad_call(c)]

            # Build test case for all metrics
            test_case = build_test_case(
                question=question,
                gold_answer=expected_output,
                actual_answer=actual_answer,
                tool_calls=tool_calls,
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
                "exact_match_eval": exact_match_score.success,
                "bad_calls": len(bad_calls),
                "total_calls": len(tool_calls),
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

def test_dual_memory(data_path: str | Path, output_path: str | Path):
    apply_env()
    df_bridge = pd.read_csv(data_path)
    print(f"Loaded data from {data_path} (length: {len(df_bridge)})")

    trace_handler = FullReActTrace() 
    agent = creat_react_agent(llm=get_llm_with_trace(trace_handler))  # Pass trace handler to get_llm_with_trace

    results = []
    total = 0
    success = 0
    exact_match_success = 0
    SAVE_PATH = Path(output_path)
    with get_database_session() as session:
        for i, row in df_bridge.iterrows():
            # Clear global tool_calls before each run
            tool_calls.clear()
            expected_output = row["answer"]
            question = row["question"]
            mem_start = time.perf_counter()
            experience_examples = retrieve_memories(question, session=session)
            mem_end = time.perf_counter()
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

                bad_calls = [c for c in tool_calls if is_bad_call(c)]

                # Build test case for all metrics
                test_case = build_test_case(
                    question=question,
                    gold_answer=expected_output,
                    actual_answer=actual_answer,
                    tool_calls=tool_calls,
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
                    "exact_match_eval": exact_match_score.success,
                    "bad_calls": len(bad_calls),
                    "total_calls": len(tool_calls),
                    # Latencies
                    "memory_latency_s": mem_end - mem_start,
                    "agent_latency_s": agent_end - agent_start,
                    "total_latency_s": (mem_end - mem_start) + (agent_end - agent_start),
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
