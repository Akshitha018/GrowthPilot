from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.experiment import ExperimentResult


router = APIRouter(
    prefix="/experiments",
    tags=["Experiment Results"]
)


# ============================================================
# ADD EXPERIMENT RESULT
# ============================================================

@router.post("/{experiment_id}/results")
def create_result(
    experiment_id: str,
    customer_id: str,
    metric: str,
    value: float,
    db: Session = Depends(get_db)
):

    result = ExperimentResult(
        result_id=str(uuid4()),
        experiment_id=experiment_id,
        customer_id=customer_id,
        metric=metric,
        value=value
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    return {
        "message": "Experiment result saved successfully",
        "result": result
    }


# ============================================================
# GET RESULTS FOR EXPERIMENT
# ============================================================

@router.get("/{experiment_id}/results")
def get_results(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    results = db.query(
        ExperimentResult
    ).filter(
        ExperimentResult.experiment_id == experiment_id
    ).all()

    return results