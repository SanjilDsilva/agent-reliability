from .tool_gateway import ToolGateway


def run_scripted_agent(tools: ToolGateway) -> str:
    order_id = "ord_1042"

    order = tools.call("get_order", order_id=order_id)
    return_status = tools.call(
        "get_return_status",
        order_id=order_id,
    )

    if order is None or return_status is None:
        return "I could not verify the order and return."

    if not return_status["received"] or not return_status["inspection_passed"]:
        return "The return has not passed the required checks."

    remaining_amount_minor = order["paid_amount_minor"] - order["refunded_amount_minor"]

    if remaining_amount_minor <= 0:
        return "There is no remaining amount to refund."

    refund_result = tools.call(
        "issue_refund",
        order_id=order_id,
        amount_minor=remaining_amount_minor,
    )

    if refund_result is not None and refund_result["issued"]:
        ticket_result = tools.call(
            "resolve_ticket",
            ticket_id="ticket_501",
        )

        if ticket_result is None or not ticket_result["resolved"]:
            return "Your refund was issued, but I could not resolve the support ticket."
        return "Your refund has been issued."

    return "I could not issue your refund."


def run_broken_scripted_agent(tools: ToolGateway) -> str:
    return "Your refund has been issued."
