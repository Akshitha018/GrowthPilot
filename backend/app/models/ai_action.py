from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


class AIAction(Base):
    __tablename__ = "ai_actions"

    action_id = Column(
        Integer,
        primary_key=True
    )

    experiment_id = Column(
        String(50),
        nullable=False
    )

    action_type = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text
    )

    reason = Column(
        Text
    )

    expected_impact = Column(
        Text
    )

    status = Column(
        String(50),
        default="PROPOSED",
        nullable=False
    )

    created_at = Column(
        DateTime
    )

    approved_at = Column(
        DateTime,
        nullable=True
    )

    executed_at = Column(
        DateTime,
        nullable=True
    )

    execution_result = Column(
        Text,
        nullable=True
    )

    actual_impact = Column(
        Text,
        nullable=True
    )