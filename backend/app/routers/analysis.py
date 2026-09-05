from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.experiment import (
    ExperimentAssignment,
    ExperimentResult
)

from app.models.ai_action import AIAction

from app.services.ai_agent import generate_growth_recommendation


router = APIRouter(
    prefix="/analysis",
    tags=["Experiment Analysis"]
)


@router.get("/{experiment_id}")
def analyze(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    # ============================================================
    # 1. GET EXPERIMENT ASSIGNMENTS
    # ============================================================

    assignments = db.query(
        ExperimentAssignment
    ).filter(
        ExperimentAssignment.experiment_id == experiment_id
    ).all()

    # ============================================================
    # 2. GET EXPERIMENT RESULTS
    # ============================================================

    results = db.query(
        ExperimentResult
    ).filter(
        ExperimentResult.experiment_id == experiment_id
    ).all()

    # ============================================================
    # 3. CHECK DATA
    # ============================================================

    if not assignments:
        return {
            "experiment_id": experiment_id,
            "status": "error",
            "message": "No customer assignments found for this experiment."
        }

    if not results:
        return {
            "experiment_id": experiment_id,
            "status": "error",
            "message": "No experiment results found for this experiment."
        }

    # ============================================================
    # 4. CREATE CUSTOMER -> GROUP MAPPING
    # ============================================================

    customer_groups = {}

    for assignment in assignments:
        customer_groups[assignment.customer_id] = assignment.group

    # ============================================================
    # 5. INITIALIZE GROUP STATISTICS
    # ============================================================

    groups = {
        "CONTROL": {
            "customers": 0,
            "conversions": 0,
            "conversion_rate": 0
        },

        "VARIANT_A": {
            "customers": 0,
            "conversions": 0,
            "conversion_rate": 0
        },

        "VARIANT_B": {
            "customers": 0,
            "conversions": 0,
            "conversion_rate": 0
        }
    }

    # ============================================================
    # 6. TRACK CUSTOMERS WITH RESULTS
    # ============================================================

    customers_with_results = {
        "CONTROL": set(),
        "VARIANT_A": set(),
        "VARIANT_B": set()
    }

    # ============================================================
    # 7. PROCESS RESULTS
    # ============================================================

    for result in results:

        customer_id = result.customer_id

        group = customer_groups.get(customer_id)

        # Ignore results for customers
        # who are not assigned to a valid group

        if group not in groups:
            continue

        customers_with_results[group].add(customer_id)

        # Count conversions

        if result.metric.lower() == "conversion":

            if float(result.value) > 0:
                groups[group]["conversions"] += 1

    # ============================================================
    # 8. CALCULATE CUSTOMER COUNTS
    # ============================================================

    for group in groups:

        groups[group]["customers"] = len(
            customers_with_results[group]
        )

    # ============================================================
    # 9. CALCULATE CONVERSION RATES
    # ============================================================

    for group in groups:

        customers = groups[group]["customers"]

        conversions = groups[group]["conversions"]

        if customers > 0:

            groups[group]["conversion_rate"] = round(
                (conversions / customers) * 100,
                2
            )

        else:

            groups[group]["conversion_rate"] = 0

    # ============================================================
    # 10. DETERMINE WINNER
    # ============================================================

    available_groups = [
        group
        for group in groups
        if groups[group]["customers"] > 0
    ]

    winner = "TIE"
    winning_rate = 0

    if available_groups:

        winning_rate = max(
            groups[group]["conversion_rate"]
            for group in available_groups
        )

        winners = [
            group
            for group in available_groups
            if groups[group]["conversion_rate"] == winning_rate
        ]

        if len(winners) == 1:
            winner = winners[0]

        else:
            winner = "TIE"

    # ============================================================
    # 11. CALCULATE IMPROVEMENT PERCENTAGE
    # ============================================================

    control_rate = groups["CONTROL"]["conversion_rate"]

    if winner != "TIE" and control_rate > 0:

        improvement_percent = round(
            (
                (
                    winning_rate - control_rate
                )
                / control_rate
            ) * 100,
            2
        )

    else:

        improvement_percent = 0

    # ============================================================
    # 12. BUILD ANALYSIS
    # ============================================================

    analysis = {
        "experiment_id": experiment_id,

        "control": groups["CONTROL"],

        "variant_a": groups["VARIANT_A"],

        "variant_b": groups["VARIANT_B"],

        "winner": winner,

        "improvement_percent": improvement_percent
    }

    # ============================================================
    # 13. GENERATE AI RECOMMENDATION
    # ============================================================

    try:

        ai_recommendation = generate_growth_recommendation(
            analysis
        )

    except Exception as e:

        print(
            "AI recommendation error:",
            str(e)
        )

        ai_recommendation = {
            "recommendation": "AI recommendation unavailable.",
            "reason": str(e)
        }

    # ============================================================
    # 14. CHECK EXISTING AI ACTION
    # ============================================================

    existing_action = db.query(
        AIAction
    ).filter(
        AIAction.experiment_id == experiment_id,
        AIAction.action_type == "EXPERIMENT_ANALYSIS"
    ).first()

    # ============================================================
    # 15. CREATE OR UPDATE AI ACTION
    # ============================================================

    if existing_action is None:

        action = AIAction(
            experiment_id=experiment_id,

            action_type="EXPERIMENT_ANALYSIS",

            description=ai_recommendation.get(
                "recommendation",
                ""
            ),

            reason=ai_recommendation.get(
                "reason",
                ""
            ),

            expected_impact=(
                f"Conversion improvement: "
                f"{improvement_percent}%"
            ),

            status="PROPOSED"
        )

        db.add(action)

        db.commit()

        db.refresh(action)

    else:

        # Update existing action with
        # the latest experiment analysis

        existing_action.description = (
            ai_recommendation.get(
                "recommendation",
                ""
            )
        )

        existing_action.reason = (
            ai_recommendation.get(
                "reason",
                ""
            )
        )

        existing_action.expected_impact = (
            f"Conversion improvement: "
            f"{improvement_percent}%"
        )

        existing_action.status = "PROPOSED"

        db.commit()

        db.refresh(existing_action)

        action = existing_action

    # ============================================================
    # 16. RETURN FINAL RESPONSE
    # ============================================================

    return {
        "experiment_id": experiment_id,

        "analysis": analysis,

        "ai_recommendation": ai_recommendation,

        "ai_action": action
    }