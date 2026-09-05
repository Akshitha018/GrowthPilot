from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random

from app.database import get_db
from app.models.experiment import ExperimentAssignment
from app.models.customer import Customer
from app.models.experiment import Experiment


router = APIRouter(
    prefix="/experiment-assignments",
    tags=["Experiment Assignments"]
)


# ---------------------------------------------------------
# MANUAL ASSIGNMENT
# ---------------------------------------------------------

@router.post("/")
def create_assignment(
    assignment: dict,
    db: Session = Depends(get_db)
):

    experiment_id = assignment["experiment_id"]
    customer_id = assignment["customer_id"]
    group = assignment["group"]

    # Check whether experiment exists
    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()

    if not experiment:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    # Check whether customer exists
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # Check whether this customer is already assigned
    existing_assignment = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id == experiment_id,
        ExperimentAssignment.customer_id == customer_id
    ).first()

    if existing_assignment:
        return {
            "message": "Customer already assigned",
            "assignment": {
                "experiment_id": existing_assignment.experiment_id,
                "customer_id": existing_assignment.customer_id,
                "group": existing_assignment.group
            }
        }

    # Validate group
    allowed_groups = ["CONTROL", "VARIANT_A", "VARIANT_B"]

    if group not in allowed_groups:
        raise HTTPException(
            status_code=400,
            detail="Group must be CONTROL, VARIANT_A, or VARIANT_B"
        )

    # Create assignment
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


# ---------------------------------------------------------
# AUTOMATIC CUSTOMER ASSIGNMENT
# ---------------------------------------------------------

@router.post("/auto/{experiment_id}")
def auto_assign_customers(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    # Check experiment
    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()

    if not experiment:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    # Get all customers
    customers = db.query(Customer).all()


    if not customers:
        raise HTTPException(
            status_code=404,
            detail="No customers found"
        )

    # Get customers already assigned
    existing_assignments = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id == experiment_id
    ).all()

    assigned_customer_ids = {
        assignment.customer_id
        for assignment in existing_assignments
    }

    # Only assign customers who are not already assigned
    unassigned_customers = [
        customer
        for customer in customers
        if customer.customer_id not in assigned_customer_ids
    ]

    if not unassigned_customers:
        return {
            "message": "All customers are already assigned",
            "experiment_id": experiment_id,
            "total_assigned": len(existing_assignments)
        }

    # Shuffle customers
    random.shuffle(unassigned_customers)

    groups = ["CONTROL", "VARIANT_A", "VARIANT_B"]

    new_assignments = []

    # Assign customers approximately equally
    for index, customer in enumerate(unassigned_customers):

        group = groups[index % 3]

        new_assignment = ExperimentAssignment(
            experiment_id=experiment_id,
            customer_id=customer.customer_id,
            group=group
        )

        db.add(new_assignment)
        new_assignments.append(new_assignment)

    db.commit()

    # Count groups
    control_count = sum(
        1 for assignment in new_assignments
        if assignment.group == "CONTROL"
    )

    variant_a_count = sum(
        1 for assignment in new_assignments
        if assignment.group == "VARIANT_A"
    )

    variant_b_count = sum(
        1 for assignment in new_assignments
        if assignment.group == "VARIANT_B"
    )

    return {
        "message": "Customers assigned successfully",
        "experiment_id": experiment_id,
        "new_customers_assigned": len(new_assignments),
        "groups": {
            "CONTROL": control_count,
            "VARIANT_A": variant_a_count,
            "VARIANT_B": variant_b_count
        }
    }


# ---------------------------------------------------------
# GET ASSIGNMENTS
# ---------------------------------------------------------

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