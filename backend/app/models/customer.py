from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(50), primary_key=True)
    age = Column(Integer)
    gender = Column(String(20))
    city = Column(String(100))
    segment = Column(String(50))
    total_orders = Column(Integer, default=0)
    total_spent = Column(Numeric(12, 2), default=0)
    aov = Column(Numeric(12, 2), default=0)
    last_purchase = Column(DateTime)