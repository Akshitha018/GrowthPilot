from sqlalchemy import Column, String, ForeignKey, Float, DateTime
from app.database import Base


class Experiment(Base):
    __tablename__ = "experiments"

    experiment_id = Column(
        String,
        primary_key=True
    )

    name = Column(
        String,
        nullable=False
    )

    hypothesis = Column(
        String,
        nullable=True
    )

    objective = Column(
        String,
        nullable=True
    )

    target_segment = Column(
        String,
        nullable=True
    )

    control_description = Column(
        String,
        nullable=True
    )

    variant_a_description = Column(
        String,
        nullable=True
    )

    variant_b_description = Column(
        String,
        nullable=True
    )

    status = Column(
        String,
        nullable=False,
        default="DRAFT"
    )
    
    winner = Column(
    String,
    nullable=True
    )

    budget = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=True
    )


class ExperimentAssignment(Base):
    __tablename__ = "experiment_assignments"

    experiment_id = Column(
        String,
        ForeignKey("experiments.experiment_id"),
        primary_key=True
    )

    customer_id = Column(
        String,
        ForeignKey("customers.customer_id"),
        primary_key=True
    )

    group = Column(
        String,
        nullable=False
    )


class ExperimentResult(Base):
    __tablename__ = "experiment_results"

    result_id = Column(
        String,
        primary_key=True
    )

    experiment_id = Column(
        String,
        ForeignKey("experiments.experiment_id"),
        nullable=False
    )

    customer_id = Column(
        String,
        ForeignKey("customers.customer_id"),
        nullable=False
    )

    metric = Column(
        String,
        nullable=False
    )

    value = Column(
        Float,
        nullable=False
    )

    created_at = Column(
        DateTime
    )