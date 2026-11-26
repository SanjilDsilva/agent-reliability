from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class EvaluationAttempt(Base):
    __tablename__ = "evaluation_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    batch_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True,
    )
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    trace_events: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    agent_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluation_result: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
