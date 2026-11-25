from typing import Any

from .database import SessionFactory
from .models import EvaluationAttempt


def save_evaluation_attempt(
    task_id: str,
    agent_response: str,
    trace_events: list[dict[str, Any]],
    evaluation_result: dict[str, Any],
) -> int:
    attempt = EvaluationAttempt(
        task_id=task_id,
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
            "agent_response": attempt.agent_response,
            "trace_events": attempt.trace_events,
            "evaluation_result": attempt.evaluation_result,
        }
