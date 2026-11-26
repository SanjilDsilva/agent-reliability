import json
from pathlib import Path

from agent_reliability.adapters.tools import execute_tool, get_langchain_tools
from agent_reliability.environment import SupportEnvironment
from agent_reliability.outcome_evaluator import evaluate_refund_task
from agent_reliability.scripted_agent import (
    run_broken_scripted_agent,
    run_scripted_agent,
)
from agent_reliability.tool_gateway import TraceRecorder, ToolGateway
from agent_reliability.evaluation_runner import run_evaluation
from agent_reliability.persistence import get_evaluation_attempt

TASKS_DIR = Path(__file__).resolve().parents[1] / "tasks"
TASK_1 = TASKS_DIR / "refund_eligible_001.json"
TASK_2 = TASKS_DIR / "refund_denied_002.json"
TASK_3 = TASKS_DIR / "wrong_customer_003.json"


def test_broken_scripted_fails_all_three_tasks():
    """Verify that a broken agent making zero tool calls fails all 3 tasks."""
    for task_path in [TASK_1, TASK_2, TASK_3]:
        with task_path.open(encoding="utf-8") as f:
            task = json.load(f)

        env = SupportEnvironment(
            task["environment_fixture"],
            task["agent_input"]["authenticated_customer_id"],
            task["reviewer_behavior"],
        )
        trace = TraceRecorder()
        tools = ToolGateway(env, trace)

        run_broken_scripted_agent(tools)

        eval_result = evaluate_refund_task(
            environment_state=env.evaluator_snapshot(),
            expected_amount_minor=task["evaluation"]["expected_refund_total_minor"],
            expected_ticket_status=task["evaluation"]["expected_ticket_status"],
            trace_events=list(trace.events),
            required_tool_calls=task["evaluation"].get("required_tool_calls"),
        )
        assert eval_result["passed"] is False


def test_good_scripted_passes_all_three_tasks():
    """Verify that a rule-abiding scripted agent passes all 3 tasks."""
    for task_path in [TASK_1, TASK_2, TASK_3]:
        with task_path.open(encoding="utf-8") as f:
            task = json.load(f)

        env = SupportEnvironment(
            task["environment_fixture"],
            task["agent_input"]["authenticated_customer_id"],
            task["reviewer_behavior"],
        )
        trace = TraceRecorder()
        tools = ToolGateway(env, trace)

        run_scripted_agent(tools)

        eval_result = evaluate_refund_task(
            environment_state=env.evaluator_snapshot(),
            expected_amount_minor=task["evaluation"]["expected_refund_total_minor"],
            expected_ticket_status=task["evaluation"]["expected_ticket_status"],
            trace_events=list(trace.events),
            required_tool_calls=task["evaluation"].get("required_tool_calls"),
        )
        assert eval_result["passed"] is True


def test_both_adapters_return_identical_error_json_for_missing_order():
    """Contract test: both adapters return identical JSON on missing order."""

    class FakeGateway:
        def call(self, name, **kwargs):
            if kwargs.get("order_id") == "ord_missing":
                return None
            return {"status": "ok"}

    fake = FakeGateway()

    # 1. Plain Gemini adapter path
    plain_result = execute_tool(fake, "get_order", order_id="ord_missing")

    # 2. LangGraph adapter path
    langgraph_tools = get_langchain_tools(fake)
    get_order_tool = next(t for t in langgraph_tools if t.name == "get_order")
    langgraph_result = get_order_tool.invoke({"order_id": "ord_missing"})

    assert plain_result == {"error": "not_found_or_unauthorized"}
    assert langgraph_result == {"error": "not_found_or_unauthorized"}
    assert plain_result == langgraph_result


def test_bad_arguments_do_not_crash_and_return_structured_error():
    """Contract test: calling tools with unexpected arguments returns structured error."""

    class FakeGateway:
        def call(self, name, **kwargs):
            if "bad_arg" in kwargs:
                raise TypeError("unexpected keyword argument bad_arg")
            return {"status": "ok"}

    fake = FakeGateway()
    result = execute_tool(fake, "issue_refund", bad_arg=123)
    assert result["error"] == "invalid_arguments"
    assert "bad_arg" in result["detail"]


def test_crash_saved_as_status_error_and_persisted():
    """Contract test: an agent exception is saved with status 'error' in DB."""

    class FlakyAgent:
        name = "mock_flaky_agent"
        model_name = "mock_flash_lite"

        def run(self, prompt, tools):
            raise ConnectionError("Simulated 503 Google API high demand")

    result = run_evaluation(
        TASK_1,
        FlakyAgent(),
        batch_id="batch_contract_test",
        max_retries=0,
    )

    assert result["status"] == "error"
    assert "Simulated 503" in result["error_message"]

    attempt = get_evaluation_attempt(result["attempt_id"])
    assert attempt is not None
    assert attempt["status"] == "error"
    assert attempt["batch_id"] == "batch_contract_test"
    assert attempt["agent_id"] == "mock_flaky_agent"
