import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.experiment import Experiment
from app.services.experiment_generator import generate_experiment


router = APIRouter(
    prefix="/generator",
    tags=["AI Experiment Generator"]
)


@router.post("/")
def generate(
    goal: str,
    target_segment: str,
    db: Session = Depends(get_db)
):

    # --------------------------------
    # 1. Validate input
    # --------------------------------

    if not goal or not goal.strip():
        raise HTTPException(
            status_code=400,
            detail="Goal is required"
        )

    if not target_segment or not target_segment.strip():
        raise HTTPException(
            status_code=400,
            detail="Target segment is required"
        )


    # --------------------------------
    # 2. Generate experiment details
    # --------------------------------

    try:

        experiment_data = generate_experiment(
            goal,
            target_segment
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate experiment: {str(e)}"
        )


    # --------------------------------
    # 3. Generate unique experiment ID
    # --------------------------------

    experiment_id = (
        "EXP-" +
        uuid.uuid4().hex[:8].upper()
    )


    # --------------------------------
    # 4. Create database record
    # --------------------------------

    experiment = Experiment(
        experiment_id=experiment_id,
        name=experiment_data["name"],
        hypothesis=experiment_data["hypothesis"],
        objective=experiment_data["objective"],
        target_segment=experiment_data["target_segment"],
        control_description=experiment_data["control_description"],
        variant_a_description=experiment_data["variant_a_description"],
        variant_b_description=experiment_data["variant_b_description"],
        status=experiment_data["status"],
        budget=experiment_data["budget"]
    )


    # --------------------------------
    # 5. Save experiment to database
    # --------------------------------

    try:

        db.add(experiment)

        db.commit()

        db.refresh(experiment)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save experiment: {str(e)}"
        )


    # --------------------------------
    # 6. Return successful response
    # --------------------------------

    return {
        "message": "Experiment generated and saved",
        "experiment": experiment
    }