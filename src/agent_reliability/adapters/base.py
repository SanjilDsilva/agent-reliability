from typing import Protocol
from ..tool_gateway import ToolGateway

class AgentAdapter(Protocol):
    """This standard contract every agent must satisfy to be evaluated."""

    name: str

    def run(self, prompt: str, tools: ToolGateway) -> str:
        """
        Executes the agent given the user's prompt.
        Must execute all environment actions exclusively through the provided 'tools' gateway.
        Returns the final agent response string.
        """
        ...