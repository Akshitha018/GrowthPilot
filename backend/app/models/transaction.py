from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), nullable=False)
    product_id = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    discount = Column(Numeric(12, 2), default=0)
    revenue = Column(Numeric(12, 2), nullable=False)
    timestamp = Column(DateTime)