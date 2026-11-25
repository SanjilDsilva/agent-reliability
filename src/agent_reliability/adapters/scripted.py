from ..scripted_agent import run_scripted_agent, run_broken_scripted_agent
from ..tool_gateway import ToolGateway


class ScriptedGoodAgentAdapter:
    name: str = "good_scripted"

    def run(self, prompt: str, tools: ToolGateway) -> str:
        # Prompt is ignored because this baseline is hardcoded
        return run_scripted_agent(tools)


class ScriptedBrokenAgentAdapter:
    name: str = "broken_scripted"

    def run(self, prompt: str, tools: ToolGateway) -> str:
        # Claims success without calling any tools
        return run_broken_scripted_agent(tools)
