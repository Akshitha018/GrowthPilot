from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100))
    price = Column(Numeric(12, 2), nullable=False)
    cost = Column(Numeric(12, 2), nullable=False)
    stock = Column(Integer, default=0)