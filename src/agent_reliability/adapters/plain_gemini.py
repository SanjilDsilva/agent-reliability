import json
import os
from typing import Any
from dotenv import load_dotenv
from openai import OpenAI

from ..tool_gateway import ToolGateway
from .tools import SUPPORTED_TOOL_SCHEMAS

load_dotenv()

SYSTEM_PROMPT = """You are a helpful customer support agent for an e-commerce store.
Your goal is to assist the customer with their order, return, or refund request.

Strict Guidelines:
1. Check order details and return inspection status before issuing any refund.
2. Only issue a refund if the return has been received and passed warehouse inspection.
3. The refund amount must be the unpaid remaining balance in minor currency units (paise/cents).
4. Resolve the support ticket after issuing the refund.
5. Execute actions exclusively using the provided tools. Once completed, provide a clear summary message to the customer.
"""


class PlainGeminiAdapter:
    """Zero-framework agent loop running against Gemini's free OpenAI-compatible endpoint."""

    name: str = "plain_gemini"

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash",
        max_steps: int = 8,
        client: Any = None,
    ):
        self.model_name = model_name
        self.max_steps = max_steps

        if client is not None:
            self.client = client
        else:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY not found. Please set GEMINI_API_KEY in your private .env file."
                )
            # Google's official OpenAI-compatible endpoint
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )

    def run(self, prompt: str, tools: ToolGateway) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        for _ in range(self.max_steps):
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=SUPPORTED_TOOL_SCHEMAS,
            )

            message = response.choices[0].message
            messages.append(message)

            # If Gemini didn't call any tools, it's done talking
            if not message.tool_calls:
                return message.content or ""

            # Execute each tool call through the gateway camera
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                result = tools.call(tool_name, **tool_args)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result if result is not None else {}),
                    }
                )

        return "Agent stopped: reached maximum allowed tool-call steps."
