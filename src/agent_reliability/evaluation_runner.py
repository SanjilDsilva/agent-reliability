import json
from pathlib import Path
import time
from typing import Any, Callable, Union

from .environment import SupportEnvironment
from .outcome_evaluator import evaluate_refund_task
from .tool_gateway import TraceRecorder, ToolGateway
from .persistence import save_evaluation_attempt
from .adapters.base import AgentAdapter

# Supports either an AgentAdapter object or a legacy function callable
AgentTarget = Union[AgentAdapter, Callable[[ToolGateway], str]]


def run_evaluation(
    task_path: Path,
    agent: AgentTarget,
    batch_id: str | None = None,
    max_retries: int = 2,
) -> dict[str, Any]:
    with task_path.open(encoding="utf-8") as task_file:
        task = json.load(task_file)

    user_message = task["agent_input"]["user_message"]
    customer_id = task["agent_input"]["authenticated_customer_id"]

    agent_id = getattr(agent, "name", getattr(agent, "__name__", "unknown"))
    model_name = getattr(agent, "model_name", None)

    environment = SupportEnvironment(
        task["environment_fixture"],
        customer_id,
        task["reviewer_behavior"],
    )

    trace = TraceRecorder()
    tools = ToolGateway(environment, trace)

    agent_response: str | None = None
    status: str | None = None
    error_message: str | None = None
    evaluation_result: dict[str, Any] | None = None

    for attempt_num in range(max_retries + 1):
        try:
            if hasattr(agent, "run"):
                agent_response = agent.run(user_message, tools)
            else:
                agent_response = agent(tools)
            break
        except Exception as exc:
            if attempt_num < max_retries:
                time.sleep(1.0 * (2**attempt_num))  # Backoff: 1s, then 2s
            else:
                status = "error"
                error_message = str(exc)
                agent_response = f"Execution error: {exc}"
    trace_events = list(trace.events)
    if status != "error":
        evaluation_result = evaluate_refund_task(
            environment.evaluator_snapshot(),
            task["evaluation"]["expected_refund_total_minor"],
            task["evaluation"]["expected_ticket_status"],
            trace_events=trace_events,
            required_tool_calls=task["evaluation"].get("required_tool_calls"),
        )
        status = "passed" if evaluation_result.get("passed") else "failed"
    attempt_id = save_evaluation_attempt(
        task_id=task["id"],
        agent_response=agent_response,
        trace_events=trace_events,
        evaluation_result=evaluation_result,
        agent_id=agent_id,
        model_name=model_name,
        batch_id=batch_id,
        status=status,
        error_message=error_message,
    )
    return {
        "task_id": task["id"],
        "agent_id": agent_id,
        "model_name": model_name,
        "batch_id": batch_id,
        "status": status,
        "error_message": error_message,
        "agent_response": agent_response,
        "attempt_id": attempt_id,
        "trace_events": trace_events,
        "evaluation_result": evaluation_result,
    }
