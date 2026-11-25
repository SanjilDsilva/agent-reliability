from typing import Any


def evaluate_refund_task(
    environment_state: dict[str, Any],
    expected_amount_minor: int,
    expected_ticket_status: str,
) -> dict[str, Any]:
    order = environment_state["order"]
    actual_amount_minor = order["refunded_amount_minor"]
    actual_ticket_status = environment_state["ticket"]["status"]
    refund_matches = actual_amount_minor == expected_amount_minor
    ticket_matches = actual_ticket_status == expected_ticket_status
    passed = refund_matches and ticket_matches

    return {
        "passed": passed,
        "expected_amount_minor": expected_amount_minor,
        "actual_amount_minor": actual_amount_minor,
        "expected_ticket_status": expected_ticket_status,
        "actual_ticket_status": actual_ticket_status,
    }
