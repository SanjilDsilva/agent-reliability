SUPPORTED_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "Look up an order by order ID to check paid amount, refunded amount, and currency.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The ID of the order, e.g. ord_1042",
                    }
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_return_status",
            "description": "Check if the returned items for an order have been received and passed warehouse inspection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "The ID of the order"}
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "issue_refund",
            "description": "Issue a monetary refund for an order in minor currency units (paise/cents).",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The ID of the order",
                    },
                    "amount_minor": {
                        "type": "integer",
                        "description": "Amount to refund in minor units (e.g. 249900)",
                    },
                },
                "required": ["order_id", "amount_minor"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "resolve_ticket",
            "description": "Mark a customer support ticket as resolved after completing all requested actions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "The ID of the support ticket, e.g. ticket_501",
                    }
                },
                "required": ["ticket_id"],
            },
        },
    },
]
