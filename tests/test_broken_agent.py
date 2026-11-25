import json
from pathlib import Path

from agent_reliability.environment import SupportEnvironment
from agent_reliability.outcome_evaluator import evaluate_refund_task
from agent_reliability.scripted_agent import (
    run_broken_scripted_agent,
    run_scripted_agent,
)
from agent_reliability.tool_gateway import TraceRecorder, ToolGateway


def test_broken_agent_claim_fails_when_no_refund_happens():
    task_path = (
        Path(__file__).resolve().parents[1] / "tasks" / "refund_eligible_001.json"
    )

    with task_path.open(encoding="utf-8") as task_file:
        task = json.load(task_file)

    environment = SupportEnvironment(
        task["environment_fixture"],
        task["agent_input"]["authenticated_customer_id"],
        task["reviewer_behavior"],
    )

    trace = TraceRecorder()
    tools = ToolGateway(environment, trace)

    response = run_broken_scripted_agent(tools)
    result = evaluate_refund_task(
        environment.evaluator_snapshot(),
        task["evaluation"]["expected_refund_total_minor"],
        task["evaluation"]["expected_ticket_status"],
    )

    assert response == "Your refund has been issued."
    assert result["passed"] is False
    assert result["actual_amount_minor"] == 0
    assert trace.events == ()


def test_good_agent_issues_refund_and_is_recorded():
    task_path = (
        Path(__file__).resolve().parents[1] / "tasks" / "refund_eligible_001.json"
    )

    with task_path.open(encoding="utf-8") as task_file:
        task = json.load(task_file)

    environment = SupportEnvironment(
        task["environment_fixture"],
        task["agent_input"]["authenticated_customer_id"],
        task["reviewer_behavior"],
    )
    trace = TraceRecorder()
    tools = ToolGateway(environment, trace)

    response = run_scripted_agent(tools)
    result = evaluate_refund_task(
        environment.evaluator_snapshot(),
        task["evaluation"]["expected_refund_total_minor"],
        task["evaluation"]["expected_ticket_status"],
    )

    assert response == "Your refund has been issued."
    assert result["passed"] is True
    assert result["actual_amount_minor"] == 249900
    assert len(trace.events) == 4
    assert trace.events[0]["tool_name"] == "get_order"
    assert trace.events[1]["tool_name"] == "get_return_status"
    assert trace.events[2]["tool_name"] == "issue_refund"
    assert trace.events[3]["tool_name"] == "resolve_ticket"
    assert (
        environment.evaluator_snapshot()["ticket"]["status"]
        == task["evaluation"]["expected_ticket_status"]
    )


def test_refund_is_rejected_when_reviewer_denies():
    task_path = (
        Path(__file__).resolve().parents[1] / "tasks" / "refund_eligible_001.json"
    )

    with task_path.open(encoding="utf-8") as task_file:
        task = json.load(task_file)

    task["reviewer_behavior"]["decision"] = "deny"

    environment = SupportEnvironment(
        task["environment_fixture"],
        task["agent_input"]["authenticated_customer_id"],
        task["reviewer_behavior"],
    )
    trace = TraceRecorder()
    tools = ToolGateway(environment, trace)

    order = task["environment_fixture"]["order"]
    result = tools.call(
        "issue_refund",
        order_id=order["id"],
        amount_minor=order["paid_amount_minor"],
    )

    assert result == {"issued": False, "reason": "reviewer_denied"}
    assert environment.evaluator_snapshot()["order"]["refunded_amount_minor"] == 0
    assert trace.events[0]["result"] == result


def test_other_customer_cannot_read_or_refund_order():
    task_path = (
        Path(__file__).resolve().parents[1] / "tasks" / "refund_eligible_001.json"
    )

    with task_path.open(encoding="utf-8") as task_file:
        task = json.load(task_file)

    other_customer_id = "cust_99"
    environment = SupportEnvironment(
        task["environment_fixture"],
        other_customer_id,
        task["reviewer_behavior"],
    )
    trace = TraceRecorder()
    tools = ToolGateway(environment, trace)

    order = task["environment_fixture"]["order"]
    read_result = tools.call("get_order", order_id=order["id"])
    refund_result = tools.call(
        "issue_refund",
        order_id=order["id"],
        amount_minor=order["paid_amount_minor"],
    )
    ticket_result = tools.call(
        "resolve_ticket",
        ticket_id=task["environment_fixture"]["ticket"]["id"],
    )

    assert read_result is None
    assert refund_result is None
    assert environment.evaluator_snapshot()["order"]["refunded_amount_minor"] == 0
    assert trace.events[0]["result"] is None
    assert trace.events[1]["result"] is None
    assert ticket_result is None
    assert environment.evaluator_snapshot()["ticket"]["status"] == "open"
    assert trace.events[2]["result"] is None


def test_duplicate_refund_does_not_refund_twice():
    task_path = (
        Path(__file__).resolve().parents[1] / "tasks" / "refund_eligible_001.json"
    )

    with task_path.open(encoding="utf-8") as task_file:
        task = json.load(task_file)

    environment = SupportEnvironment(
        task["environment_fixture"],
        task["agent_input"]["authenticated_customer_id"],
        task["reviewer_behavior"],
    )
    trace = TraceRecorder()
    tools = ToolGateway(environment, trace)
    order = task["environment_fixture"]["order"]

    first_result = tools.call(
        "issue_refund",
        order_id=order["id"],
        amount_minor=order["paid_amount_minor"],
    )
    second_result = tools.call(
        "issue_refund",
        order_id=order["id"],
        amount_minor=order["paid_amount_minor"],
    )

    assert first_result == {"issued": True, "amount_minor": 249900}
    assert second_result == {
        "issued": False,
        "reason": "invalid_or_duplicate_amount",
    }
    assert (
        environment.evaluator_snapshot()["order"]["refunded_amount_minor"]
        == order["paid_amount_minor"]
    )
    assert len(trace.events) == 2
