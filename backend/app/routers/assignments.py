from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.experiment import ExperimentAssignment


router = APIRouter(
    prefix="/experiment-assignments",
    tags=["Experiment Assignments"]
)


@router.post("/")
def create_assignment(
    assignment: dict,
    db: Session = Depends(get_db)
):

    experiment_id = assignment["experiment_id"]
    customer_id = assignment["customer_id"]
    group = assignment["group"]

    # Check whether this customer is already assigned
    existing_assignment = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id == experiment_id,
        ExperimentAssignment.customer_id == customer_id
    ).first()

    # If already assigned, return the existing assignment
    if existing_assignment:

        return {
            "message": "Customer already assigned",
            "assignment": {
                "experiment_id": existing_assignment.experiment_id,
                "customer_id": existing_assignment.customer_id,
                "group": existing_assignment.group
            }
        }

    # Create new assignment
    new_assignment = ExperimentAssignment(
        experiment_id=experiment_id,
        customer_id=customer_id,
        group=group
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return {
        "message": "Customer assigned successfully",
        "assignment": {
            "experiment_id": new_assignment.experiment_id,
            "customer_id": new_assignment.customer_id,
            "group": new_assignment.group
        }
    }


@router.get("/{experiment_id}")
def get_assignments(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    assignments = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id == experiment_id
    ).all()

    return assignments