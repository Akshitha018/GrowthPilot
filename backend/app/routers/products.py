from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get("/")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products


@router.get("/{product_id}")
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        return {"message": "Product not found"}

    return product


@router.post("/")
def create_product(
    product: dict,
    db: Session = Depends(get_db)
):
    new_product = Product(
        product_id=product["product_id"],
        name=product["name"],
        category=product.get("category"),
        price=product["price"],
        cost=product["cost"],
        stock=product.get("stock", 0)
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product