import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evaluation_runner import run_evaluation
from .scripted_agent import run_scripted_agent, run_broken_scripted_agent
from .adapters.plain_gemini import PlainGeminiAdapter
from .adapters.langgraph_adapter import LangGraphAdapter

TASKS_DIR = Path(__file__).resolve().parents[2] / "tasks"

TASK_FILES = [
    TASKS_DIR / "refund_eligible_001.json",
    TASKS_DIR / "refund_denied_002.json",
    TASKS_DIR / "wrong_customer_003.json",
]


def run_batch(repeats: int = 5, batch_id: str | None = None) -> str:
    if batch_id is None:
        batch_id = f"batch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    print(f"\n==========================================")
    print(f"Starting Benchmark Batch: {batch_id}")
    print(f"Repeats per test: {repeats}")
    print(f"==========================================\n")

    # 1. Run controls (sanity checks: good should pass, broken should fail)
    print("--- Running Controls ---")
    controls = [
        ("good_scripted", run_scripted_agent),
        ("broken_scripted", run_broken_scripted_agent),
    ]
    for task_path in TASK_FILES:
        for name, agent in controls:
            result = run_evaluation(task_path, agent, batch_id=batch_id)
            print(f"CONTROL | {task_path.stem:<20} | {name:<16} -> {result['status']}")

    # 2. Run target agents for N repeats
    print("\n--- Running Target Agents ---")
    agents = [
        PlainGeminiAdapter(),
        LangGraphAdapter(),
    ]

    total_runs = len(TASK_FILES) * len(agents) * repeats
    current_run = 0

    for rep in range(1, repeats + 1):
        for task_path in TASK_FILES:
            for agent in agents:
                current_run += 1
                result = run_evaluation(task_path, agent, batch_id=batch_id)
                tools_used = len(result.get("trace_events", []))
                print(
                    f"[{current_run:>2}/{total_runs}] rep {rep}/{repeats} | "
                    f"{task_path.stem:<20} | {agent.name:<16} -> {result['status']:<6} "
                    f"(tools: {tools_used})"
                )

    print(f"\n==========================================")
    print(f"Batch completed: {batch_id}")
    print(f"==========================================\n")
    return batch_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Agent Reliability Benchmark Batch"
    )
    parser.add_argument(
        "--repeats", type=int, default=5, help="Number of repeats per task per agent"
    )
    parser.add_argument(
        "--batch-id", type=str, default=None, help="Custom batch identifier"
    )
    args = parser.parse_args()

    run_batch(repeats=args.repeats, batch_id=args.batch_id)
