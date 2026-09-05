from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
import random

from app.database import get_db

from app.models.experiment import (
    Experiment,
    ExperimentAssignment,
    ExperimentResult
)

from app.models.customer import Customer
from app.models.ai_action import AIAction
from app.models.transaction import Transaction

from app.services.decision_engine import make_growth_decision
from app.services.ai_growth_agent import generate_growth_recommendation


router = APIRouter(
    prefix="/experiments",
    tags=["Experiments"]
)


MAX_CUSTOMERS_PER_EXPERIMENT = 100


# ============================================================
# GET ALL EXPERIMENTS
# ============================================================

@router.get("/")
def get_experiments(
    db: Session = Depends(get_db)
):

    experiments = db.query(Experiment).all()

    return experiments


# ============================================================
# GET ONE EXPERIMENT
# ============================================================

@router.get("/{experiment_id}")
def get_experiment(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()

    if not experiment:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    return experiment


# ============================================================
# CREATE EXPERIMENT
# ============================================================

@router.post("/")
def create_experiment(
    experiment: dict,
    db: Session = Depends(get_db)
):

    required_fields = [
        "experiment_id",
        "name"
    ]

    for field in required_fields:

        if not experiment.get(field):

            raise HTTPException(
                status_code=400,
                detail=f"{field} is required"
            )

    existing_experiment = db.query(
        Experiment
    ).filter(
        Experiment.experiment_id ==
        experiment["experiment_id"]
    ).first()

    if existing_experiment:

        raise HTTPException(
            status_code=400,
            detail="Experiment ID already exists"
        )

    new_experiment = Experiment(
        experiment_id=experiment["experiment_id"],
        name=experiment["name"],
        hypothesis=experiment.get("hypothesis"),
        objective=experiment.get("objective"),
        target_segment=experiment.get("target_segment"),
        control_description=experiment.get(
            "control_description"
        ),
        variant_a_description=experiment.get(
            "variant_a_description"
        ),
        variant_b_description=experiment.get(
            "variant_b_description"
        ),
        status=experiment.get(
            "status",
            "DRAFT"
        ),
        budget=experiment.get(
            "budget",
            0
        ),
        created_at=experiment.get(
            "created_at"
        )
    )

    try:

        db.add(new_experiment)

        db.commit()

        db.refresh(new_experiment)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create experiment: {str(e)}"
        )

    return new_experiment


# ============================================================
# UPDATE EXPERIMENT STATUS
# ============================================================

@router.patch("/{experiment_id}/status")
def update_experiment_status(
    experiment_id: str,
    status: str,
    db: Session = Depends(get_db)
):

    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    allowed_statuses = [
        "DRAFT",
        "ACTIVE",
        "COMPLETED",
        "WINNER_SELECTED"
    ]

    status = status.strip().upper()

    if status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid experiment status '{status}'. "
                f"Allowed statuses are: "
                f"{', '.join(allowed_statuses)}"
            )
        )

    experiment.status = status

    try:

        db.commit()

        db.refresh(experiment)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to update experiment status: {str(e)}"
        )

    return {
        "message": "Experiment status updated",
        "experiment": experiment
    }


# ============================================================
# ACTIVATE EXPERIMENT
# ============================================================

@router.patch("/{experiment_id}/activate")
def activate_experiment(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    if experiment.status == "ACTIVE":

        return {
            "message": "Experiment is already active",
            "experiment_id": experiment_id,
            "status": experiment.status
        }

    if experiment.status != "DRAFT":

        raise HTTPException(
            status_code=400,
            detail=(
                f"Experiment cannot be activated "
                f"because its current status is "
                f"{experiment.status}"
            )
        )

    experiment.status = "ACTIVE"

    try:

        db.commit()

        db.refresh(experiment)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to activate experiment: {str(e)}"
        )

    return {
        "message": "Experiment activated successfully",
        "experiment_id": experiment.experiment_id,
        "status": experiment.status
    }


# ============================================================
# COMPLETE EXPERIMENT
# ============================================================

@router.patch("/{experiment_id}/complete")
def complete_experiment(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    if experiment.status == "COMPLETED":

        return {
            "message": "Experiment is already completed",
            "experiment_id": experiment_id,
            "status": experiment.status
        }

    if experiment.status != "ACTIVE":

        raise HTTPException(
            status_code=400,
            detail=(
                f"Experiment cannot be completed "
                f"because its current status is "
                f"{experiment.status}. "
                f"Activate the experiment first."
            )
        )

    results = db.query(
        ExperimentResult
    ).filter(
        ExperimentResult.experiment_id ==
        experiment_id
    ).all()

    if not results:

        raise HTTPException(
            status_code=400,
            detail="Cannot complete experiment without results"
        )

    experiment.status = "COMPLETED"

    try:

        db.commit()

        db.refresh(experiment)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete experiment: {str(e)}"
        )

    return {
        "message": "Experiment completed successfully",
        "experiment_id": experiment_id,
        "status": experiment.status
    }


# ============================================================
# SELECT WINNER
# ============================================================

@router.patch("/{experiment_id}/winner")
def select_winner(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    if experiment.status == "WINNER_SELECTED":

        return {
            "message": "Winner has already been selected",
            "experiment_id": experiment_id,
            "winner": experiment.winner,
            "status": experiment.status
        }

    if experiment.status != "COMPLETED":

        raise HTTPException(
            status_code=400,
            detail=(
                f"Winner cannot be selected because the "
                f"experiment status is {experiment.status}. "
                f"Complete the experiment first."
            )
        )

    assignments = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id ==
        experiment_id
    ).all()

    results = db.query(
        ExperimentResult
    ).filter(
        ExperimentResult.experiment_id ==
        experiment_id
    ).all()

    if not assignments:

        raise HTTPException(
            status_code=400,
            detail="No customer assignments found"
        )

    if not results:

        raise HTTPException(
            status_code=400,
            detail="No experiment results found"
        )

    groups = {}

    for assignment in assignments:

        group = assignment.group

        if group not in groups:

            groups[group] = {
                "customers": 0,
                "conversions": 0,
                "conversion_rate": 0
            }

        groups[group]["customers"] += 1

    for result in results:

        if result.metric != "conversion":
            continue

        assignment = db.query(
            ExperimentAssignment
        ).filter(
            ExperimentAssignment.experiment_id ==
            experiment_id,
            ExperimentAssignment.customer_id ==
            result.customer_id
        ).first()

        if assignment and result.value > 0:

            groups[assignment.group]["conversions"] += 1

    for group in groups:

        customers = groups[group]["customers"]

        conversions = groups[group]["conversions"]

        if customers > 0:

            groups[group]["conversion_rate"] = round(
                (conversions / customers) * 100,
                2
            )

    winner = max(
        groups,
        key=lambda group:
        groups[group]["conversion_rate"]
    )

    experiment.winner = winner

    experiment.status = "WINNER_SELECTED"

    try:

        db.commit()

        db.refresh(experiment)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to select winner: {str(e)}"
        )

    return {
        "message": "Winner selected successfully",
        "experiment_id": experiment_id,
        "winner": experiment.winner,
        "status": experiment.status,
        "groups": groups
    }


# ============================================================
# GET EXPERIMENT ASSIGNMENTS
# ============================================================

@router.get("/{experiment_id}/assignments")
def get_assignments(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    assignments = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id ==
        experiment_id
    ).limit(MAX_CUSTOMERS_PER_EXPERIMENT).all()

    return assignments


# ============================================================
# ASSIGN CUSTOMERS TO A/B GROUPS
# ============================================================

@router.post("/{experiment_id}/assign")
def assign_customers(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    # --------------------------------------------------------
    # Check existing assignments
    # --------------------------------------------------------

    existing_assignments = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id ==
        experiment_id
    ).all()

    existing_count = len(existing_assignments)

    # --------------------------------------------------------
    # Never allow more than 100 customers
    # --------------------------------------------------------

    if existing_count >= MAX_CUSTOMERS_PER_EXPERIMENT:

        return {
            "message": "100 customers are already assigned",
            "experiment_id": experiment_id,
            "customers_assigned": existing_count,
            "assignments": existing_assignments[:100]
        }

    # --------------------------------------------------------
    # Existing customer IDs
    # --------------------------------------------------------

    assigned_customer_ids = {
        assignment.customer_id
        for assignment in existing_assignments
    }

    # --------------------------------------------------------
    # Get only unassigned customers
    # --------------------------------------------------------

    unassigned_customers = db.query(
        Customer
    ).filter(
        ~Customer.customer_id.in_(
            assigned_customer_ids
        )
    ).all()

    if not unassigned_customers:

        raise HTTPException(
            status_code=404,
            detail="No unassigned customers available"
        )

    # --------------------------------------------------------
    # Calculate remaining slots
    # --------------------------------------------------------

    remaining_slots = (
        MAX_CUSTOMERS_PER_EXPERIMENT
        - existing_count
    )

    sample_size = min(
        remaining_slots,
        len(unassigned_customers)
    )

    selected_customers = random.sample(
        unassigned_customers,
        sample_size
    )

    # --------------------------------------------------------
    # Groups
    # --------------------------------------------------------

    groups = [
        "CONTROL",
        "VARIANT_A",
        "VARIANT_B"
    ]

    new_assignments = []

    # --------------------------------------------------------
    # Assign customers
    # --------------------------------------------------------

    for index, customer in enumerate(
        selected_customers
    ):

        group = groups[index % len(groups)]

        assignment = ExperimentAssignment(
            experiment_id=experiment_id,
            customer_id=customer.customer_id,
            group=group
        )

        db.add(assignment)

        new_assignments.append({
            "customer_id": customer.customer_id,
            "group": group
        })

    try:

        db.commit()

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to assign customers: {str(e)}"
        )

    total_assigned = existing_count + sample_size

    return {
        "message": (
            "100 customers assigned successfully"
            if total_assigned == 100
            else f"{total_assigned} customers assigned successfully"
        ),
        "experiment_id": experiment_id,
        "customers_assigned": total_assigned,
        "new_customers_assigned": sample_size,
        "assignments": new_assignments
    }


# ============================================================
# RECORD EXPERIMENT RESULT
# ============================================================

@router.post("/{experiment_id}/results")
def record_result(
    experiment_id: str,
    customer_id: str,
    metric: str,
    value: float,
    db: Session = Depends(get_db)
):

    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    assignment = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id ==
        experiment_id,
        ExperimentAssignment.customer_id ==
        customer_id
    ).first()

    if not assignment:

        raise HTTPException(
            status_code=404,
            detail="Customer is not assigned to this experiment"
        )

    metric = metric.strip().lower()

    if metric != "conversion":

        raise HTTPException(
            status_code=400,
            detail="Allowed metric: conversion"
        )

    if value < 0:

        raise HTTPException(
            status_code=400,
            detail="Result value cannot be negative"
        )

    if metric == "conversion" and value not in [0, 1]:

        raise HTTPException(
            status_code=400,
            detail="Conversion value must be either 0 or 1"
        )

    existing_result = db.query(
        ExperimentResult
    ).filter(
        ExperimentResult.experiment_id ==
        experiment_id,
        ExperimentResult.customer_id ==
        customer_id,
        ExperimentResult.metric ==
        metric
    ).first()

    if existing_result:

        return {
            "message": "Experiment result already exists",
            "result_id": existing_result.result_id
        }

    result = ExperimentResult(
        result_id=str(uuid4()),
        experiment_id=experiment_id,
        customer_id=customer_id,
        metric=metric,
        value=value,
        created_at=datetime.utcnow()
    )

    try:

        db.add(result)

        db.commit()

        db.refresh(result)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save experiment result: {str(e)}"
        )

    return {
        "message": "Experiment result recorded",
        "experiment_id": experiment_id,
        "customer_id": customer_id,
        "group": assignment.group,
        "metric": metric,
        "value": value,
        "result_id": result.result_id
    }


# ============================================================
# GET EXPERIMENT RESULTS
# ============================================================

@router.get("/{experiment_id}/results")
def get_results(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    results = db.query(
        ExperimentResult
    ).filter(
        ExperimentResult.experiment_id ==
        experiment_id
    ).all()

    return results


# ============================================================
# GENERATE EXPERIMENT RESULTS
# ============================================================

@router.post("/{experiment_id}/generate-results")
def generate_experiment_results(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    assignments = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id ==
        experiment_id
    ).limit(MAX_CUSTOMERS_PER_EXPERIMENT).all()

    if not assignments:

        raise HTTPException(
            status_code=404,
            detail="No customers assigned to this experiment"
        )

    created_results = 0

    for assignment in assignments:

        existing_result = db.query(
            ExperimentResult
        ).filter(
            ExperimentResult.experiment_id ==
            experiment_id,
            ExperimentResult.customer_id ==
            assignment.customer_id,
            ExperimentResult.metric ==
            "conversion"
        ).first()

        if existing_result:

            continue

        transaction = db.query(
            Transaction
        ).filter(
            Transaction.customer_id ==
            assignment.customer_id
        ).first()

        conversion_value = 1 if transaction else 0

        result = ExperimentResult(
            result_id=str(uuid4()),
            experiment_id=experiment_id,
            customer_id=assignment.customer_id,
            metric="conversion",
            value=conversion_value,
            created_at=datetime.utcnow()
        )

        db.add(result)

        created_results += 1

    try:

        db.commit()

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate results: {str(e)}"
        )

    return {
        "message": "Experiment results generated successfully",
        "experiment_id": experiment_id,
        "results_created": created_results
    }


# ============================================================
# RUN EXPERIMENT
# ============================================================

@router.post("/{experiment_id}/run")
def run_experiment(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # 1. Check experiment
    # --------------------------------------------------------

    experiment = db.query(
        Experiment
    ).filter(
        Experiment.experiment_id ==
        experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    # --------------------------------------------------------
    # 2. Get maximum 100 assignments
    # --------------------------------------------------------

    assignments = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id ==
        experiment_id
    ).limit(
        MAX_CUSTOMERS_PER_EXPERIMENT
    ).all()

    if not assignments:

        raise HTTPException(
            status_code=404,
            detail="No customers assigned to this experiment"
        )

    # --------------------------------------------------------
    # 3. Generate conversion results
    # --------------------------------------------------------

    results_created = 0

    for assignment in assignments:

        existing_result = db.query(
            ExperimentResult
        ).filter(
            ExperimentResult.experiment_id ==
            experiment_id,
            ExperimentResult.customer_id ==
            assignment.customer_id,
            ExperimentResult.metric ==
            "conversion"
        ).first()

        if existing_result:

            continue

        transaction = db.query(
            Transaction
        ).filter(
            Transaction.customer_id ==
            assignment.customer_id
        ).first()

        conversion_value = (
            1 if transaction else 0
        )

        result = ExperimentResult(
            result_id=str(uuid4()),
            experiment_id=experiment_id,
            customer_id=assignment.customer_id,
            metric="conversion",
            value=conversion_value,
            created_at=datetime.utcnow()
        )

        db.add(result)

        results_created += 1

    try:

        db.commit()

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate experiment results: {str(e)}"
        )

    # --------------------------------------------------------
    # 4. Calculate conversion rates
    # --------------------------------------------------------

    groups = [
        "CONTROL",
        "VARIANT_A",
        "VARIANT_B"
    ]

    analysis = {}

    for group in groups:

        group_assignments = [
            assignment
            for assignment in assignments
            if assignment.group == group
        ]

        total = len(group_assignments)

        if total == 0:

            analysis[group] = {
                "customers": 0,
                "conversions": 0,
                "conversion_rate": 0
            }

            continue

        customer_ids = [
            assignment.customer_id
            for assignment in group_assignments
        ]

        conversions = db.query(
            ExperimentResult
        ).filter(
            ExperimentResult.experiment_id ==
            experiment_id,
            ExperimentResult.metric ==
            "conversion",
            ExperimentResult.customer_id.in_(
                customer_ids
            ),
            ExperimentResult.value == 1
        ).count()

        conversion_rate = (
            conversions / total
        ) * 100

        analysis[group] = {
            "customers": total,
            "conversions": conversions,
            "conversion_rate": round(
                conversion_rate,
                2
            )
        }

    # --------------------------------------------------------
    # 5. Select winner
    # --------------------------------------------------------

    winner = max(
        analysis,
        key=lambda group:
        analysis[group]["conversion_rate"]
    )

    # --------------------------------------------------------
    # 6. Update experiment
    # --------------------------------------------------------

    experiment.status = "WINNER_SELECTED"

    experiment.winner = winner

    try:

        db.commit()

        db.refresh(experiment)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to update experiment: {str(e)}"
        )

    # --------------------------------------------------------
    # 7. Return complete result
    # --------------------------------------------------------

    return {
        "message": "Experiment completed successfully",
        "experiment_id": experiment_id,
        "status": experiment.status,
        "winner": winner,
        "results_created": results_created,
        "customers_processed": len(assignments),
        "analysis": analysis
    }


# ============================================================
# ANALYZE EXPERIMENT
# ============================================================

@router.get("/{experiment_id}/analysis")
def analyze_experiment(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    experiment = db.query(
        Experiment
    ).filter(
        Experiment.experiment_id ==
        experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    assignments = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id ==
        experiment_id
    ).limit(
        MAX_CUSTOMERS_PER_EXPERIMENT
    ).all()

    if not assignments:

        raise HTTPException(
            status_code=404,
            detail="No customers assigned to this experiment"
        )

    groups = {}

    for assignment in assignments:

        group = assignment.group

        if group not in groups:

            groups[group] = {
                "customers": [],
                "conversions": 0
            }

        groups[group]["customers"].append(
            assignment.customer_id
        )

    results = db.query(
        ExperimentResult
    ).filter(
        ExperimentResult.experiment_id ==
        experiment_id,
        ExperimentResult.metric ==
        "conversion"
    ).all()

    for result in results:

        if result.value <= 0:
            continue

        for group_name, group_data in groups.items():

            if result.customer_id in group_data["customers"]:

                group_data["conversions"] += 1

                break

    for group_name, group_data in groups.items():

        total_customers = len(
            group_data["customers"]
        )

        conversions = group_data["conversions"]

        if total_customers > 0:

            conversion_rate = (
                conversions / total_customers
            ) * 100

        else:

            conversion_rate = 0

        group_data["conversion_rate"] = round(
            conversion_rate,
            2
        )

    winner = max(
        groups,
        key=lambda group:
        groups[group]["conversion_rate"]
    )

    control_rate = groups.get(
        "CONTROL",
        {}
    ).get(
        "conversion_rate",
        0
    )

    winner_rate = groups[winner]["conversion_rate"]

    if control_rate > 0:

        improvement = (
            (winner_rate - control_rate)
            / control_rate
        ) * 100

    else:

        improvement = 0

    return {
        "experiment_id": experiment_id,
        "groups": groups,
        "winner": winner,
        "improvement_percent": round(
            improvement,
            2
        )
    }


# ============================================================
# AI GROWTH DECISION
# ============================================================

@router.get("/{experiment_id}/decision")
def get_growth_decision(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    experiment = db.query(
        Experiment
    ).filter(
        Experiment.experiment_id ==
        experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    assignments = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id ==
        experiment_id
    ).limit(
        MAX_CUSTOMERS_PER_EXPERIMENT
    ).all()

    if not assignments:

        raise HTTPException(
            status_code=404,
            detail="No customers assigned"
        )

    results = db.query(
        ExperimentResult
    ).filter(
        ExperimentResult.experiment_id ==
        experiment_id,
        ExperimentResult.metric ==
        "conversion"
    ).all()

    groups = {}

    for assignment in assignments:

        if assignment.group not in groups:

            groups[assignment.group] = {
                "customers": [],
                "conversions": 0
            }

        groups[
            assignment.group
        ]["customers"].append(
            assignment.customer_id
        )

    for result in results:

        if result.value <= 0:
            continue

        for group_name, group in groups.items():

            if result.customer_id in group["customers"]:

                group["conversions"] += 1

                break

    for group_name, group in groups.items():

        total = len(group["customers"])

        if total > 0:

            group["conversion_rate"] = round(
                (group["conversions"] / total) * 100,
                2
            )

        else:

            group["conversion_rate"] = 0

    winner = max(
        groups,
        key=lambda g:
        groups[g]["conversion_rate"]
    )

    control_rate = groups.get(
        "CONTROL",
        {}
    ).get(
        "conversion_rate",
        0
    )

    winner_rate = groups[winner]["conversion_rate"]

    if control_rate > 0:

        improvement = (
            (winner_rate - control_rate)
            / control_rate
        ) * 100

    else:

        improvement = 0

    analysis = {
        "experiment_id": experiment_id,
        "groups": groups,
        "winner": winner,
        "improvement_percent": round(
            improvement,
            2
        )
    }

    decision = make_growth_decision(
        analysis
    )

    return {
        "experiment": experiment.name,
        "analysis": analysis,
        "ai_decision": decision
    }


# ============================================================
# AI GROWTH RECOMMENDATION
# ============================================================

@router.get("/{experiment_id}/ai-recommendation")
def get_ai_recommendation(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    experiment = db.query(
        Experiment
    ).filter(
        Experiment.experiment_id ==
        experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    assignments = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id ==
        experiment_id
    ).limit(
        MAX_CUSTOMERS_PER_EXPERIMENT
    ).all()

    if not assignments:

        raise HTTPException(
            status_code=404,
            detail="No customers assigned"
        )

    results = db.query(
        ExperimentResult
    ).filter(
        ExperimentResult.experiment_id ==
        experiment_id,
        ExperimentResult.metric ==
        "conversion"
    ).all()

    groups = {}

    for assignment in assignments:

        group_name = assignment.group

        if group_name not in groups:

            groups[group_name] = {
                "customers": [],
                "conversions": 0
            }

        groups[group_name]["customers"].append(
            assignment.customer_id
        )

    for result in results:

        if result.value <= 0:
            continue

        for group_name, group in groups.items():

            if result.customer_id in group["customers"]:

                group["conversions"] += 1

                break

    for group_name, group in groups.items():

        total_customers = len(
            group["customers"]
        )

        conversions = group["conversions"]

        if total_customers > 0:

            group["conversion_rate"] = round(
                (conversions / total_customers) * 100,
                2
            )

        else:

            group["conversion_rate"] = 0

    winner = max(
        groups,
        key=lambda group:
        groups[group]["conversion_rate"]
    )

    control_rate = groups.get(
        "CONTROL",
        {}
    ).get(
        "conversion_rate",
        0
    )

    winner_rate = groups[winner]["conversion_rate"]

    if control_rate > 0:

        improvement = (
            (winner_rate - control_rate)
            / control_rate
        ) * 100

    else:

        improvement = 0

    analysis = {
        "experiment_id": experiment_id,
        "groups": groups,
        "winner": winner,
        "improvement_percent": round(
            improvement,
            2
        )
    }

    decision = make_growth_decision(
        analysis
    )

    try:

        recommendation = generate_growth_recommendation(
            experiment_name=experiment.name,
            goal=experiment.hypothesis,
            analysis=analysis,
            decision=decision
        )

    except Exception as e:

        error_message = str(e)

        if (
            "429" in error_message
            or "quota" in error_message.lower()
        ):

            recommendation = {
                "recommendation":
                    "AI recommendation temporarily unavailable.",
                "reason":
                    "The AI provider quota has been exceeded. "
                    "The experiment analysis and rule-based "
                    "decision are still available.",
                "status":
                    "QUOTA_EXCEEDED"
            }

        else:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Failed to generate AI recommendation: "
                    f"{error_message}"
                )
            )

    existing_action = db.query(
        AIAction
    ).filter(
        AIAction.experiment_id ==
        experiment_id,
        AIAction.status != "REJECTED"
    ).first()

    if not existing_action:

        if isinstance(recommendation, dict):

            description = recommendation.get(
                "recommendation",
                "Apply the winning experiment strategy."
            )

            reason = recommendation.get(
                "reason",
                "The recommendation is based on experiment performance."
            )

        else:

            description = str(
                recommendation
            )

            reason = (
                "The recommendation is based on "
                "experiment performance."
            )

        ai_action = AIAction(
            experiment_id=experiment_id,
            action_type="GROWTH_OPTIMIZATION",
            description=description,
            reason=reason,
            expected_impact=(
                f"Improve conversion by approximately "
                f"{round(improvement, 2)}%"
            ),
            status="PROPOSED",
            created_at=datetime.utcnow()
        )

        try:

            db.add(ai_action)

            db.commit()

            db.refresh(ai_action)

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Failed to create AI action: {str(e)}"
                )
            )

    else:

        ai_action = existing_action

    return {
        "experiment_id": experiment_id,
        "analysis": analysis,
        "decision": decision,
        "ai_recommendation": recommendation,
        "ai_action": ai_action
    }