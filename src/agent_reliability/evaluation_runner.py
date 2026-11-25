import json
from pathlib import Path
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
) -> dict[str, Any]:
    with task_path.open(encoding="utf-8") as task_file:
        task = json.load(task_file)

    user_message = task["agent_input"]["user_message"]
    customer_id = task["agent_input"]["authenticated_customer_id"]

    environment = SupportEnvironment(
        task["environment_fixture"],
        customer_id,
        task["reviewer_behavior"],
    )

    trace = TraceRecorder()
    tools = ToolGateway(environment, trace)

    # If it's an AgentAdapter, call .run(user_message, tools)
    # If it's a legacy function, call agent(tools)
    if hasattr(agent, "run"):
        agent_response = agent.run(user_message, tools)
    else:
        agent_response = agent(tools)

    evaluation_result = evaluate_refund_task(
        environment.evaluator_snapshot(),
        task["evaluation"]["expected_refund_total_minor"],
        task["evaluation"]["expected_ticket_status"],
    )

    trace_events = list(trace.events)
    attempt_id = save_evaluation_attempt(
        task["id"],
        agent_response,
        trace_events,
        evaluation_result,
    )

    return {
        "task_id": task["id"],
        "agent_response": agent_response,
        "attempt_id": attempt_id,
        "trace_events": trace_events,
        "evaluation_result": evaluation_result,
    }
