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

from app.services.decision_engine import make_growth_decision
from app.services.ai_growth_agent import generate_growth_recommendation


router = APIRouter(
    prefix="/experiments",
    tags=["Experiments"]
)


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

    # --------------------------------------------------------
    # Validate required fields
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Check duplicate experiment ID
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Create experiment
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Save experiment
    # --------------------------------------------------------

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
        "experiment_id": experiment.experiment_id,
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

        assignment = db.query(
            ExperimentAssignment
        ).filter(
            ExperimentAssignment.experiment_id ==
            experiment_id,
            ExperimentAssignment.customer_id ==
            result.customer_id
        ).first()


        if assignment and result.metric == "conversion":

            group = assignment.group

            if result.value > 0:

                groups[group]["conversions"] += 1


    for group in groups:

        customers = groups[group]["customers"]

        conversions = groups[group]["conversions"]


        if customers > 0:

            groups[group]["conversion_rate"] = (
                conversions / customers
            ) * 100


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
    ).all()


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


    customers = db.query(Customer).all()


    if not customers:

        raise HTTPException(
            status_code=404,
            detail="No customers found"
        )


    assignments = []


    for customer in customers:

        existing_assignment = db.query(
            ExperimentAssignment
        ).filter(
            ExperimentAssignment.experiment_id ==
            experiment_id,
            ExperimentAssignment.customer_id ==
            customer.customer_id
        ).first()


        if existing_assignment:

            continue


        group = random.choice([
            "CONTROL",
            "VARIANT_A",
            "VARIANT_B"
        ])


        assignment = ExperimentAssignment(
            experiment_id=experiment_id,
            customer_id=customer.customer_id,
            group=group
        )


        db.add(assignment)


        assignments.append({
            "customer_id": customer.customer_id,
            "group": group
        })


    if not assignments:

        return {
            "message": "All customers are already assigned",
            "experiment_id": experiment_id,
            "assignments": []
        }


    try:

        db.commit()

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to assign customers: {str(e)}"
        )


    return {
        "message": "Customers assigned successfully",
        "experiment_id": experiment_id,
        "assignments": assignments
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


    allowed_metrics = [
        "conversion"
    ]


    if metric not in allowed_metrics:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid metric '{metric}'. "
                f"Allowed metrics: "
                f"{', '.join(allowed_metrics)}"
            )
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
# ANALYZE EXPERIMENT
# ============================================================

@router.get("/{experiment_id}/analysis")
def analyze_experiment(
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


        customer_id = result.customer_id


        for group_name, group_data in groups.items():

            if customer_id in group_data["customers"]:

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

    # --------------------------------------------------------
    # Get experiment
    # --------------------------------------------------------

    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()


    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )


    # --------------------------------------------------------
    # Get assignments
    # --------------------------------------------------------

    assignments = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id ==
        experiment_id
    ).all()


    if not assignments:

        raise HTTPException(
            status_code=404,
            detail="No customers assigned"
        )


    # --------------------------------------------------------
    # Get conversion results
    # --------------------------------------------------------

    results = db.query(
        ExperimentResult
    ).filter(
        ExperimentResult.experiment_id ==
        experiment_id,
        ExperimentResult.metric ==
        "conversion"
    ).all()


    # --------------------------------------------------------
    # Build groups
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Count conversions
    # --------------------------------------------------------

    for result in results:

        if result.value <= 0:

            continue


        for group_name, group in groups.items():

            if result.customer_id in group["customers"]:

                group["conversions"] += 1

                break


    # --------------------------------------------------------
    # Calculate conversion rates
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Find winner
    # --------------------------------------------------------

    winner = max(
        groups,
        key=lambda group:
        groups[group]["conversion_rate"]
    )


    # --------------------------------------------------------
    # Compare with control
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Build analysis
    # --------------------------------------------------------

    analysis = {
        "experiment_id": experiment_id,
        "groups": groups,
        "winner": winner,
        "improvement_percent": round(
            improvement,
            2
        )
    }


    # --------------------------------------------------------
    # Rule-based decision
    # --------------------------------------------------------

    decision = make_growth_decision(
        analysis
    )


    # --------------------------------------------------------
    # Generate AI recommendation
    # --------------------------------------------------------

    try:

        recommendation = generate_growth_recommendation(
            experiment_name=experiment.name,
            goal=experiment.hypothesis,
            analysis=analysis,
            decision=decision
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to generate AI recommendation: {str(e)}"
            )
        )


    # ========================================================
    # CREATE AI GROWTH ACTION
    # ========================================================

    # --------------------------------------------------------
    # Check whether an action already exists
    # --------------------------------------------------------

    existing_action = db.query(
        AIAction
    ).filter(
        AIAction.experiment_id == experiment_id,
        AIAction.status != "REJECTED"
    ).first()


    # --------------------------------------------------------
    # Create action only if one does not already exist
    # --------------------------------------------------------

    if not existing_action:

        # Handle recommendation safely
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


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {
        "experiment_id": experiment_id,
        "analysis": analysis,
        "decision": decision,
        "ai_recommendation": recommendation,
        "ai_action": ai_action
    }