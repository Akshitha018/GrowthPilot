from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.transaction import Transaction

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


@router.get("/")
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    return transactions


@router.get("/{transaction_id}")
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id
    ).first()

    if not transaction:
        return {"message": "Transaction not found"}

    return transaction


@router.post("/")
def create_transaction(
    transaction: dict,
    db: Session = Depends(get_db)
):
    new_transaction = Transaction(
        transaction_id=transaction["transaction_id"],
        customer_id=transaction["customer_id"],
        product_id=transaction["product_id"],
        quantity=transaction["quantity"],
        price=transaction["price"],
        discount=transaction.get("discount", 0),
        revenue=transaction["revenue"],
        timestamp=transaction.get("timestamp")
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction