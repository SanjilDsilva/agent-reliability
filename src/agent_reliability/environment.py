from copy import deepcopy
from typing import Any


class SupportEnvironment:
    def __init__(
        self,
        fixture: dict[str, Any],
        customer_id: str,
        reviewer_behavior: dict[str, Any],
    ) -> None:
        self._state = deepcopy(fixture)
        self._customer_id = customer_id
        self._reviewer_behavior = deepcopy(reviewer_behavior)

    def _get_owned_order(
        self,
        order_id: str,
    ) -> dict[str, Any] | None:
        order = self._state["order"]

        if order["id"] != order_id or order["customer_id"] != self._customer_id:
            return None
        return order

    def get_order(self, order_id: str) -> dict[str, Any] | None:
        order = self._get_owned_order(order_id)

        if order is None:
            return None

        return {
            "id": order["id"],
            "paid_amount_minor": order["paid_amount_minor"],
            "refunded_amount_minor": order["refunded_amount_minor"],
            "currency": order["currency"],
        }

    def get_return_status(self, order_id: str) -> dict[str, bool] | None:
        order = self._get_owned_order(order_id)

        if order is None:
            return None

        return {
            "received": self._state["return"]["received"],
            "inspection_passed": self._state["return"]["inspection_passed"],
        }

    def issue_refund(
        self,
        order_id: str,
        amount_minor: int,
    ) -> dict[str, Any] | None:
        order = self._get_owned_order(order_id)
        if order is None:
            return None

        return_status = self._state["return"]
        reviewer_approved = self._reviewer_behavior["decision"] == "approve"
        if not return_status["received"] or not return_status["inspection_passed"]:
            return {"issued": False, "reason": "return_not_eligible"}

        if not reviewer_approved:
            return {"issued": False, "reason": "reviewer_denied"}

        remaining_amount_minor = (
            order["paid_amount_minor"] - order["refunded_amount_minor"]
        )

        if remaining_amount_minor <= 0 or amount_minor != remaining_amount_minor:
            return {"issued": False, "reason": "invalid_or_duplicate_amount"}

        order["refunded_amount_minor"] += amount_minor
        return {"issued": True, "amount_minor": amount_minor}

    def evaluator_snapshot(self) -> dict[str, Any]:
        return deepcopy(self._state)

    def resolve_ticket(
        self,
        ticket_id: str,
    ) -> dict[str, bool] | None:
        ticket = self._state["ticket"]

        if ticket["id"] != ticket_id or ticket["customer_id"] != self._customer_id:
            return None

        ticket["status"] = "resolved"
        return {"resolved": True}
