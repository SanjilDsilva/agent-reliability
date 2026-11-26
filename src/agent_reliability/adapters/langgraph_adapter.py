import os
from typing import Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.errors import GraphRecursionError
from .tools import get_langchain_tools
from .config import MODEL_NAME, TEMPERATURE, MAX_STEPS, SYSTEM_PROMPT
from ..tool_gateway import ToolGateway

load_dotenv()


class LangGraphAdapter:
    """Agent implementation using LangGraph state graph with Gemini 3.1 Flash Lite."""

    name: str = "Langgraph_gemini"

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        max_steps: int = MAX_STEPS,
        temperature: float = TEMPERATURE,
    ):
        self.model_name = model_name
        self.max_steps = max_steps
        self.temperature = temperature

    def run(self, prompt: str, tools: ToolGateway) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or .env file.")

        tool_list = get_langchain_tools(tools)

        # Initialize the model and bind the tools
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
            temperature=self.temperature,
        )
        llm_with_tools = llm.bind_tools(tool_list)

        # Node: Call Model
        def call_model(state: MessagesState):
            response = llm_with_tools.invoke(state["messages"])
            return {"messages": [response]}

        # Node: Tool Execution
        tool_node = ToolNode(tool_list)

        # Build the Graph
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", tool_node)

        # Edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", tools_condition)
        workflow.add_edge("tools", "agent")

        # Compile with built-in recursion limit
        app = workflow.compile()

        try:
            final_state = app.invoke(
                {
                    "messages": [
                        SystemMessage(content=SYSTEM_PROMPT),
                        HumanMessage(content=prompt),
                    ]
                },
                config={"recursion_limit": 2 * self.max_steps + 1},
            )
        except GraphRecursionError:
            return "Agent stopped: reached maximum allowed tool-call steps."

        final_message = final_state["messages"][-1]
        content = final_message.content
        if isinstance(content, list):
            return "".join(
                b.get("text", "") if isinstance(b, dict) else str(b) for b in content
            )
        return str(content or "")
