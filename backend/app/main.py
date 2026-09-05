from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from app.database import engine

from app.database import Base

from app.models import customer
from app.models import product
from app.models import transaction
from app.models import experiment
from app.models import ai_action

from app.routers.customers import router as customers_router
from app.routers.products import router as products_router
from app.routers.transactions import router as transactions_router
from app.routers.experiments import router as experiments_router
from app.routers.assignments import router as assignments_router
from app.routers.results import router as results_router
from app.routers.ai_actions import router as ai_actions_router
from app.routers.analysis import router as analysis_router
from app.routers.generator import router as generator_router


# ============================================================
# CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="GrowthPilot API",
    version="1.0.0"
)

# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)

# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
       "https://growthpilot-frontend.onrender.com"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(customers_router)

app.include_router(products_router)

app.include_router(transactions_router)

app.include_router(experiments_router)

app.include_router(assignments_router)

app.include_router(results_router)

app.include_router(ai_actions_router)

app.include_router(analysis_router)

app.include_router(generator_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "GrowthPilot API is running"
    }


# ============================================================
# DATABASE TEST
# ============================================================

@app.get("/database-test")
def database_test():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT 1")
            )

            result.fetchone()

        return {
            "status": "success",
            "message": "PostgreSQL connection successful"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }