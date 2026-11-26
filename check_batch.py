from sqlalchemy import func, select
from agent_reliability.database import SessionFactory
from agent_reliability.models import EvaluationAttempt

BATCH_ID = "batch_20261126_080707"

with SessionFactory() as session:
    rows = session.execute(
        select(
            EvaluationAttempt.agent_id,
            EvaluationAttempt.status,
            func.count(EvaluationAttempt.id),
        )
        .where(EvaluationAttempt.batch_id == BATCH_ID)
        .group_by(EvaluationAttempt.agent_id, EvaluationAttempt.status)
        .order_by(EvaluationAttempt.agent_id)
    ).all()

    print(f"\n--- Batch Counts: {BATCH_ID} ---")
    for agent_id, status, count in rows:
        print(f"{agent_id:<18} | {status:<8} | count: {count}")
