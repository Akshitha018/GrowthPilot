from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.get("/")
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()

    return customers