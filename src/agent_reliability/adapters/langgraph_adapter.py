import os
from typing import Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from ..tool_gateway import ToolGateway

load_dotenv()

SYSTEM_PROMPT = """You are a helpful customer support agent for an e-commerce store.
Your goal is to assist the customer with their order, return, or refund request.
Strict Guidelines:
1. Check order details and return inspection status before issuing any refund.
2. Only issue a refund if the return has been received and passed warehouse inspection.
3. The refund amount must be the unpaid remaining balance in minor currency units (paise/cents).
4. Resolve the support ticket after issuing the refund.
5. If an order lookup returns an error or is not found/unauthorized, do not repeatedly retry. Explain the issue clearly to the customer.
"""


class LangGraphAdapter:
    """Agent implementation using LangGraph state graph with Gemini 3.1 Flash Lite."""

    name: str = "Langgraph_gemini"

    def __init__(
        self,
        model_name: str = "gemini-3.1-flash-lite",
    ):
        self.model_name = model_name

    def run(self, prompt: str, tools: ToolGateway) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or .env file.")

        # Wrap our gateway tools so LangGraph can manage them
        @tool
        def get_order(order_id: str) -> dict:
            """Look up an order by order ID to check paid amount, refunded amount, and currency."""
            res = tools.call("get_order", order_id=order_id)
            return (
                res if res is not None else {"error": "Order not found or unauthorized"}
            )

        @tool
        def get_return_status(order_id: str) -> dict:
            """Check if returned items for an order have been recieved and passed warehouse inspection."""
            res = tools.call("get_return_status", order_id=order_id)
            return res if res is not None else {"error": "Return status not found"}

        @tool
        def issue_refund(order_id: str, amount_minor: int) -> dict:
            """Issue a refund for an order in minor currency units (paise/cents)."""
            res = tools.call(
                "issue_refund", order_id=order_id, amount_minor=amount_minor
            )
            return res if res is not None else {"error": "Failed to issue refund"}

        @tool
        def resolve_ticket(ticket_id: str) -> dict:
            """Mark a customer support ticket as resolved after completing all requested actions."""
            res = tools.call("resolve_ticket", ticket_id=ticket_id)
            return res if res is not None else {"error": "Failed to resolve ticket"}

        tool_list = [get_order, get_return_status, issue_refund, resolve_ticket]

        # Initialize the model and bind the tools
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
            temperature=0.0,
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

        final_state = app.invoke(
            {
                "messages": [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=prompt),
                ]
            },
        )

        final_message = final_state["messages"][-1]
        return final_message.content or ""
