import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path

# -----------------------------
# CONFIGURATION
# -----------------------------

NUM_CUSTOMERS = 50000
NUM_PRODUCTS = 500
NUM_TRANSACTIONS = 150000

random.seed(42)
np.random.seed(42)

DATA_DIR = Path("../data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# CUSTOMER DATA
# -----------------------------

print("Generating customers...")

customers = []

cities = [
    "Jaipur",
    "Delhi",
    "Mumbai",
    "Bangalore",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Kolkata",
    "Ahmedabad",
    "Lucknow"
]

genders = ["Male", "Female", "Other"]

for i in range(1, NUM_CUSTOMERS + 1):

    age = np.random.randint(18, 60)

    signup_date = datetime.now() - timedelta(
        days=np.random.randint(30, 1000)
    )

    customers.append({
        "customer_id": f"C{i:05d}",
        "age": age,
        "gender": random.choice(genders),
        "city": random.choice(cities),
        "signup_date": signup_date.date()
    })

customers_df = pd.DataFrame(customers)


# -----------------------------
# PRODUCT DATA
# -----------------------------

print("Generating products...")

categories = {
    "Audio": ["Headphones", "Earbuds", "Speakers"],
    "Laptops": ["Laptop", "Laptop Stand", "Laptop Bag"],
    "Mobile": ["Smartphone", "Phone Case", "Screen Protector"],
    "Gaming": ["Gaming Mouse", "Gaming Keyboard", "Controller"],
    "Camera": ["Camera", "Memory Card", "Camera Bag"],
    "Fashion": ["Shoes", "T-Shirt", "Jeans"],
    "Accessories": ["Carrying Case", "Cable", "Charger"]
}

products = []

product_counter = 1

for category, product_types in categories.items():

    for _ in range(
        NUM_PRODUCTS // len(categories)
    ):

        product_type = random.choice(product_types)

        price = round(
            np.random.uniform(500, 15000),
            2
        )

        cost = round(
            price * np.random.uniform(0.45, 0.75),
            2
        )

        products.append({
            "product_id": f"P{product_counter:04d}",
            "product_name": f"{product_type} {product_counter}",
            "category": category,
            "price": price,
            "cost": cost,
            "stock": np.random.randint(10, 500),
            "rating": round(
                np.random.uniform(3.0, 5.0),
                1
            )
        })

        product_counter += 1

products_df = pd.DataFrame(products)


# -----------------------------
# TRANSACTION DATA
# -----------------------------

print("Generating transactions...")

transactions = []

customer_ids = customers_df["customer_id"].values
product_ids = products_df["product_id"].values

product_prices = dict(
    zip(
        products_df["product_id"],
        products_df["price"]
    )
)

start_date = datetime.now() - timedelta(days=365)

for i in range(1, NUM_TRANSACTIONS + 1):

    customer_id = random.choice(customer_ids)

    product_id = random.choice(product_ids)

    quantity = np.random.choice(
        [1, 2, 3],
        p=[0.80, 0.17, 0.03]
    )

    price = product_prices[product_id]

    # Mostly no discount
    discount = np.random.choice(
        [0, 5, 10, 15],
        p=[0.60, 0.25, 0.10, 0.05]
    )

    final_price = price * (1 - discount / 100)

    revenue = final_price * quantity

    timestamp = start_date + timedelta(
        seconds=random.randint(
            0,
            365 * 24 * 60 * 60
        )
    )

    transactions.append({
        "transaction_id": f"T{i:06d}",
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "price": round(price, 2),
        "discount": discount,
        "revenue": round(revenue, 2),
        "timestamp": timestamp
    })


transactions_df = pd.DataFrame(transactions)


# -----------------------------
# SAVE DATA
# -----------------------------

customers_df.to_csv(
    DATA_DIR / "customers.csv",
    index=False
)

products_df.to_csv(
    DATA_DIR / "products.csv",
    index=False
)

transactions_df.to_csv(
    DATA_DIR / "transactions.csv",
    index=False
)


# -----------------------------
# SUMMARY
# -----------------------------

print("\nData generation completed!")

print(
    f"Customers: {len(customers_df):,}"
)

print(
    f"Products: {len(products_df):,}"
)

print(
    f"Transactions: {len(transactions_df):,}"
)

print("\nFiles created:")
print("data/customers.csv")
print("data/products.csv")
print("data/transactions.csv")