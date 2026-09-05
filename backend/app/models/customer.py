from sqlalchemy import Column, Integer, String, Date
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(50), primary_key=True)
    age = Column(Integer)
    gender = Column(String(20))
    city = Column(String(100))
    signup_date = Column(Date)