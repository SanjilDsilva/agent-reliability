import json
import os
from typing import Any
from dotenv import load_dotenv
from openai import OpenAI

from ..tool_gateway import ToolGateway
from .tools import SUPPORTED_TOOL_SCHEMAS, execute_tool
from .config import MODEL_NAME, TEMPERATURE, MAX_STEPS, SYSTEM_PROMPT

load_dotenv()


class PlainGeminiAdapter:
    """Zero-framework agent loop running against Gemini's free OpenAI-compatible endpoint."""

    name: str = "plain_gemini"

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        max_steps: int = MAX_STEPS,
        temperature: float = TEMPERATURE,
        client: Any = None,
    ):
        self.model_name = model_name
        self.max_steps = max_steps
        self.temperature = temperature
        self.client = client

    def run(self, prompt: str, tools: ToolGateway) -> str:
        if self.client is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY not found. Please set GEMINI_API_KEY in your private .env file."
                )
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        for _ in range(self.max_steps):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=SUPPORTED_TOOL_SCHEMAS,
                    temperature=self.temperature,
                )
            except Exception as e:
                error_body = getattr(getattr(e, "response", None), "text", str(e))
                raise RuntimeError(f"Google API Response: {error_body}") from e

            message = response.choices[0].message
            messages.append(message)

            # If Gemini didn't call any tools, it's done talking
            if not message.tool_calls:
                return message.content or ""

            # Execute each tool call through the gateway camera
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                result = execute_tool(tools, tool_name, **tool_args)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

        return "Agent stopped: reached maximum allowed tool-call steps."
