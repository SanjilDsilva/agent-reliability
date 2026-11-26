from typing import Any


def evaluate_refund_task(
    environment_state: dict[str, Any],
    expected_amount_minor: int,
    expected_ticket_status: str,
    trace_events: list[dict[str, Any]] | None = None,
    required_tool_calls: list[str] | None = None,
) -> dict[str, Any]:
    order = environment_state["order"]
    actual_amount_minor = order["refunded_amount_minor"]
    actual_ticket_status = environment_state["ticket"]["status"]

    refund_matches = actual_amount_minor == expected_amount_minor
    ticket_matches = actual_ticket_status == expected_ticket_status

    # Trace rules: verify all required tool calls were actually made
    trace_matches = True
    missing_tools: list[str] = []
    if required_tool_calls:
        called_tools = {event.get("tool_name") for event in (trace_events or [])}
        for tool_name in required_tool_calls:
            if tool_name not in called_tools:
                trace_matches = False
                missing_tools.append(tool_name)

    passed = refund_matches and ticket_matches and trace_matches

    return {
        "passed": passed,
        "expected_amount_minor": expected_amount_minor,
        "actual_amount_minor": actual_amount_minor,
        "expected_ticket_status": expected_ticket_status,
        "actual_ticket_status": actual_ticket_status,
        "required_tool_calls": required_tool_calls or [],
        "missing_tool_calls": missing_tools,
        "trace_matches": trace_matches,
    }
