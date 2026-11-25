from fastapi import FastAPI, status, HTTPException
from fastapi.responses import HTMLResponse

from pathlib import Path
from typing import Any
from pydantic import BaseModel

from .adapters.plain_gemini import PlainGeminiAdapter
from .adapters.langgraph_adapter import LangGraphAdapter
from .evaluation_runner import run_evaluation
from .scripted_agent import run_scripted_agent, run_broken_scripted_agent
from .persistence import get_evaluation_attempt


app = FastAPI(title="AgentReliability")
BASE_DIR = Path(__file__).resolve().parents[2]
TASK_PATH = Path(__file__).resolve().parents[2] / "tasks" / "refund_eligible_001.json"
INDEX_PATH = BASE_DIR / "static" / "index.html"


class EvaluationRequest(BaseModel):
    task_id: str
    agent_id: str


TASK_PATH_1 = BASE_DIR / "tasks" / "refund_eligible_001.json"
TASK_PATH_2 = BASE_DIR / "tasks" / "refund_denied_002.json"
TASK_PATH_3 = BASE_DIR / "tasks" / "wrong_customer_003.json"


SUPPORTED_TASKS = {
    "refund_eligible_001": TASK_PATH_1,
    "refund_denied_002": TASK_PATH_2,
    "wrong_customer_003": TASK_PATH_3,
}

SUPPORTED_AGENTS = {
    "good_scripted": run_scripted_agent,
    "broken_scripted": run_broken_scripted_agent,
    "plain_gemini": PlainGeminiAdapter(model_name="gemini-3.1-flash-lite"),
    "langgraph_gemini": LangGraphAdapter(model_name="gemini-3.1-flash-lite"),
}


@app.get("/", response_class=HTMLResponse)
def serve_dashboard() -> str:
    if not INDEX_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard frontend not found",
        )
    return INDEX_PATH.read_text(encoding="utf-8")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/evaluations", status_code=status.HTTP_201_CREATED)
def create_evaluation(request: EvaluationRequest) -> dict[str, Any]:
    task_path = SUPPORTED_TASKS.get(request.task_id)
    if task_path is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported task_id: '{request.task_id}'. Supported tasks: {list(SUPPORTED_TASKS.keys())}",
        )

    agent_function = SUPPORTED_AGENTS.get(request.agent_id)
    if agent_function is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported agent_id: '{request.agent_id}'. Supported agents: {list(SUPPORTED_AGENTS.keys())}",
        )
    try:
        return run_evaluation(task_path, agent_function)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent evaluation error: {exc}",
        )


@app.get("/evaluations/{attempt_id}")
def read_evaluation(attempt_id: int) -> dict[str, Any]:
    attempt = get_evaluation_attempt(attempt_id)

    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation attempt not found",
        )

    return attempt
