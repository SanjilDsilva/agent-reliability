from typing import Annotated, Any
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool


def execute_tool(tools: Any, tool_name: str, **kwargs: Any) -> dict[str, Any]:
    try:
        result = tools.call(tool_name, **kwargs)
    except TypeError as exc:
        return {"error": "invalid_arguments", "detail": str(exc)}
    if result is None:
        return {"error": "not_found_or_unauthorized"}
    return result


def get_langchain_tools(tools: Any = None) -> list:
    @tool
    def get_order(
        order_id: Annotated[str, "The ID of the order, e.g. ord_1042"],
    ) -> dict:
        """Look up an order by order ID to check paid amount, refunded amount, and currency."""
        return execute_tool(tools, "get_order", order_id=order_id)

    @tool
    def get_return_status(order_id: Annotated[str, "The ID of the order"]) -> dict:
        """Check if the returned items for an order have been received and passed warehouse inspection."""
        return execute_tool(tools, "get_return_status", order_id=order_id)

    @tool
    def issue_refund(
        order_id: Annotated[str, "The ID of the order"],
        amount_minor: Annotated[int, "Amount to refund in minor units (e.g. 249900)"],
    ) -> dict:
        """Issue a monetary refund for an order in minor currency units (paise/cents)."""
        return execute_tool(
            tools, "issue_refund", order_id=order_id, amount_minor=amount_minor
        )

    @tool
    def resolve_ticket(
        ticket_id: Annotated[str, "The ID of the support ticket, e.g. ticket_501"],
    ) -> dict:
        """Mark a customer support ticket as resolved after completing all requested actions."""
        return execute_tool(tools, "resolve_ticket", ticket_id=ticket_id)

    return [get_order, get_return_status, issue_refund, resolve_ticket]


SUPPORTED_TOOL_SCHEMAS = [convert_to_openai_tool(t) for t in get_langchain_tools()]
