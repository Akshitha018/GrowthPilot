from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db

from app.models.ai_action import AIAction

from app.models.experiment import (
    Experiment,
    ExperimentAssignment,
    ExperimentResult
)


router = APIRouter(
    prefix="/ai-actions",
    tags=["AI Actions"]
)


# ============================================================
# GET ALL AI ACTIONS
# ============================================================

@router.get("/")
def get_ai_actions(
    db: Session = Depends(get_db)
):

    actions = db.query(AIAction).order_by(
        AIAction.action_id.desc()
    ).all()

    return actions


# ============================================================
# GET AI ACTION BY ID
# ============================================================

@router.get("/{action_id}")
def get_ai_action(
    action_id: int,
    db: Session = Depends(get_db)
):

    action = db.query(AIAction).filter(
        AIAction.action_id == action_id
    ).first()

    if not action:

        raise HTTPException(
            status_code=404,
            detail="AI action not found"
        )

    return action


# ============================================================
# APPROVE AI ACTION
# ============================================================

@router.put("/{action_id}/approve")
def approve_ai_action(
    action_id: int,
    db: Session = Depends(get_db)
):

    action = db.query(AIAction).filter(
        AIAction.action_id == action_id
    ).first()

    if not action:

        raise HTTPException(
            status_code=404,
            detail="AI action not found"
        )

    if action.status != "PROPOSED":

        raise HTTPException(
            status_code=400,
            detail=(
                f"Action cannot be approved because "
                f"its current status is {action.status}"
            )
        )

    action.status = "APPROVED"
    action.approved_at = datetime.utcnow()

    try:

        db.commit()
        db.refresh(action)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to approve AI action: {str(e)}"
        )

    return {
        "message": "AI action approved",
        "action": action
    }


# ============================================================
# EXECUTE AI ACTION
# ============================================================

@router.put("/{action_id}/execute")
def execute_ai_action(
    action_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # 1. Find AI action
    # --------------------------------------------------------

    action = db.query(AIAction).filter(
        AIAction.action_id == action_id
    ).first()

    if not action:

        raise HTTPException(
            status_code=404,
            detail="AI action not found"
        )


    # --------------------------------------------------------
    # 2. Action must be APPROVED
    # --------------------------------------------------------

    if action.status != "APPROVED":

        raise HTTPException(
            status_code=400,
            detail=(
                "AI action must be approved "
                "before execution"
            )
        )


    # --------------------------------------------------------
    # 3. Find experiment
    # --------------------------------------------------------

    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == action.experiment_id
    ).first()

    if not experiment:

        raise HTTPException(
            status_code=404,
            detail="Experiment associated with this action not found"
        )


    # --------------------------------------------------------
    # 4. Mark action as EXECUTING
    # --------------------------------------------------------

    action.status = "EXECUTING"

    try:

        db.commit()
        db.refresh(action)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to start execution: {str(e)}"
        )


    # --------------------------------------------------------
    # 5. Execute action
    # --------------------------------------------------------

    try:

        # ====================================================
        # GET EXPERIMENT ASSIGNMENTS
        # ====================================================

        assignments = db.query(
            ExperimentAssignment
        ).filter(
            ExperimentAssignment.experiment_id ==
            action.experiment_id
        ).all()


        if not assignments:

            raise Exception(
                "No customer assignments found for this experiment"
            )


        # ====================================================
        # GET CONVERSION RESULTS
        # ====================================================

        results = db.query(
            ExperimentResult
        ).filter(
            ExperimentResult.experiment_id ==
            action.experiment_id,

            ExperimentResult.metric ==
            "conversion"
        ).all()


        if not results:

            raise Exception(
                "No conversion results found for this experiment"
            )


        # ====================================================
        # BUILD GROUP DATA
        # ====================================================

        groups = {}


        for assignment in assignments:

            group_name = assignment.group

            if group_name not in groups:

                groups[group_name] = {
                    "customers": 0,
                    "conversions": 0
                }

            groups[group_name]["customers"] += 1


        # ====================================================
        # COUNT CONVERSIONS
        # ====================================================

        for result in results:

            if result.value <= 0:
                continue

            assignment = db.query(
                ExperimentAssignment
            ).filter(
                ExperimentAssignment.experiment_id ==
                action.experiment_id,

                ExperimentAssignment.customer_id ==
                result.customer_id
            ).first()


            if assignment:

                group_name = assignment.group

                if group_name in groups:

                    groups[group_name][
                        "conversions"
                    ] += 1


        # ====================================================
        # CALCULATE CONVERSION RATES
        # ====================================================

        for group_name, group_data in groups.items():

            customers = group_data["customers"]

            conversions = group_data["conversions"]


            if customers > 0:

                group_data["conversion_rate"] = round(
                    (conversions / customers) * 100,
                    2
                )

            else:

                group_data["conversion_rate"] = 0


        # ====================================================
        # FIND WINNER
        # ====================================================

        winner = max(
            groups,
            key=lambda group:
            groups[group]["conversion_rate"]
        )


        winner_rate = groups[
            winner
        ]["conversion_rate"]


        # ====================================================
        # GET CONTROL RATE
        # ====================================================

        control_rate = groups.get(
            "CONTROL",
            {}
        ).get(
            "conversion_rate",
            0
        )


        # ====================================================
        # CALCULATE IMPROVEMENT
        # ====================================================

        if control_rate > 0:

            improvement = (
                (winner_rate - control_rate)
                / control_rate
            ) * 100

        else:

            improvement = 0


        improvement = round(
            improvement,
            2
        )


        # ====================================================
        # BUILD EXECUTION RESULT
        # ====================================================

        action.execution_result = (
            f"Action executed successfully. "
            f"Winning group: {winner}. "
            f"Conversion rate: {winner_rate}%."
        )


        # ====================================================
        # BUILD ACTUAL IMPACT
        # ====================================================

        if winner == "CONTROL":

            action.actual_impact = (
                f"Control group performed best with "
                f"a {winner_rate}% conversion rate. "
                f"No improvement over control was observed."
            )

        else:

            action.actual_impact = (
                f"{winner} achieved a {winner_rate}% "
                f"conversion rate compared with "
                f"{control_rate}% for CONTROL. "
                f"Improvement: {improvement}%."
            )


        # ====================================================
        # MARK EXECUTED
        # ====================================================

        action.status = "EXECUTED"

        action.executed_at = datetime.utcnow()


        # ====================================================
        # SAVE
        # ====================================================

        db.commit()
        db.refresh(action)


        # ====================================================
        # RETURN
        # ====================================================

        return {
            "message": "AI action executed successfully",

            "action": action,

            "experiment_id":
                action.experiment_id,

            "winner":
                winner,

            "winner_conversion_rate":
                winner_rate,

            "control_conversion_rate":
                control_rate,

            "improvement_percent":
                improvement
        }


    # ========================================================
    # EXECUTION FAILED
    # ========================================================

    except Exception as e:

        db.rollback()

        action.status = "FAILED"

        action.execution_result = str(e)

        action.actual_impact = (
            "Execution failed. "
            "No actual impact was recorded."
        )


        try:

            db.commit()
            db.refresh(action)

        except Exception:

            db.rollback()


        return {
            "message": "AI action execution failed",
            "action": action
        }


# ============================================================
# REJECT AI ACTION
# ============================================================

@router.put("/{action_id}/reject")
def reject_ai_action(
    action_id: int,
    db: Session = Depends(get_db)
):

    action = db.query(AIAction).filter(
        AIAction.action_id == action_id
    ).first()

    if not action:

        raise HTTPException(
            status_code=404,
            detail="AI action not found"
        )


    if action.status != "PROPOSED":

        raise HTTPException(
            status_code=400,
            detail=(
                f"Action cannot be rejected because "
                f"its current status is {action.status}"
            )
        )


    action.status = "REJECTED"


    try:

        db.commit()
        db.refresh(action)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to reject AI action: {str(e)}"
        )


    return {
        "message": "AI action rejected",
        "action": action
    }