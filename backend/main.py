from fastapi import FastAPI

app = FastAPI(
    title="GrowthPilot API",
    description="AI Growth Experimentation Agent",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "GrowthPilot API is running!",
        "status": "success"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }