from typing import Any

from .environment import SupportEnvironment


class TraceRecorder:
    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def record_tool_call(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        result: Any,
    ) -> None:
        self._events.append(
            {
                "sequence": len(self._events) + 1,
                "event_type": "tool_call",
                "tool_name": tool_name,
                "arguments": arguments,
                "result": result,
            }
        )

    @property
    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._events)


class ToolGateway:
    def __init__(
        self,
        environment: SupportEnvironment,
        recorder: TraceRecorder,
    ) -> None:
        self._environment = environment
        self._recorder = recorder

    def call(
        self,
        tool_name: str,
        **arguments: Any,
    ) -> Any:
        if tool_name == "get_order":
            result = self._environment.get_order(**arguments)
        elif tool_name == "get_return_status":
            result = self._environment.get_return_status(**arguments)
        elif tool_name == "issue_refund":
            result = self._environment.issue_refund(**arguments)
        elif tool_name == "resolve_ticket":
            result = self._environment.resolve_ticket(**arguments)
        else:
            raise ValueError(f"Unsupported tool: {tool_name}")
        self._recorder.record_tool_call(
            tool_name,
            arguments,
            result,
        )
        return result
