from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

from app.api.v1 import sensors, measurements, users, alerts, admin

app = FastAPI(
    title="CleanOffice API",
    description="API for CleanOffice Air Quality Monitoring System",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(sensors.router, prefix="/api/v1", tags=["sensors"])
app.include_router(measurements.router, prefix="/api/v1", tags=["measurements"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(alerts.router, prefix="/api/v1", tags=["alerts"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["administration"])

@app.get("/")
def read_root():
    return {"message": "Welcome to CleanOffice API"}
