from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.experiment import Experiment, ExperimentAssignment
from app.models.transaction import Transaction


router = APIRouter(
    prefix="/experiments",
    tags=["Experiment Results"]
)


# ============================================================
# GET AUTOMATIC EXPERIMENT RESULTS
# ============================================================

@router.get("/{experiment_id}/results")
def get_results(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    # Check experiment exists
    experiment = db.query(Experiment).filter(
        Experiment.experiment_id == experiment_id
    ).first()

    if not experiment:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    # Calculate results for each group
    results = (
        db.query(
            ExperimentAssignment.group.label("group"),
            func.count(
                Transaction.transaction_id
            ).label("transactions"),
            func.coalesce(
                func.sum(Transaction.revenue),
                0
            ).label("revenue")
        )
        .join(
            Transaction,
            Transaction.customer_id ==
            ExperimentAssignment.customer_id
        )
        .filter(
            ExperimentAssignment.experiment_id ==
            experiment_id
        )
        .group_by(
            ExperimentAssignment.group
        )
        .all()
    )

    response = []

    for result in results:

        response.append({
            "group": result.group,
            "transactions": result.transactions,
            "revenue": float(result.revenue)
        })

    return {
        "experiment_id": experiment_id,
        "results": response
    }