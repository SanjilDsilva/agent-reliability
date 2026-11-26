from typing import Any

from .database import SessionFactory
from .models import EvaluationAttempt


def save_evaluation_attempt(
    task_id: str,
    agent_response: str,
    trace_events: list[dict[str, Any]],
    evaluation_result: dict[str, Any] | None,
    agent_id: str | None = None,
    model_name: str | None = None,
    batch_id: str | None = None,
    status: str | None = None,
    error_message: str | None = None,
) -> int:
    # If status wasn't explicitly given, derive it from the evaluator result
    if status is None and evaluation_result is not None:
        status = "passed" if evaluation_result.get("passed") else "failed"

    attempt = EvaluationAttempt(
        task_id=task_id,
        agent_id=agent_id,
        model_name=model_name,
        batch_id=batch_id,
        status=status,
        error_message=error_message,
        agent_response=agent_response,
        trace_events=trace_events,
        evaluation_result=evaluation_result,
    )

    with SessionFactory.begin() as session:
        session.add(attempt)
        session.flush()
        attempt_id = attempt.id
    return attempt_id


def get_evaluation_attempt(attempt_id: int) -> dict[str, Any] | None:
    with SessionFactory() as session:
        attempt = session.get(EvaluationAttempt, attempt_id)

        if attempt is None:
            return None

        return {
            "attempt_id": attempt.id,
            "task_id": attempt.task_id,
            "agent_id": attempt.agent_id,
            "model_name": attempt.model_name,
            "batch_id": attempt.batch_id,
            "created_at": attempt.created_at.isoformat()
            if attempt.created_at
            else None,
            "status": attempt.status,
            "error_message": attempt.error_message,
            "agent_response": attempt.agent_response,
            "trace_events": attempt.trace_events,
            "evaluation_result": attempt.evaluation_result,
        }
