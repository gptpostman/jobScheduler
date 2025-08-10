from fastapi import FastAPI
from app.api.job_routes import router as job_router
from app.database import Base, engine
from app.utils.scheduler import scheduler

app = FastAPI(
    title="Job Scheduler Microservice",
    description="API for scheduling and managing jobs.",
    version="1.0.0"
)

# Create DB tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(job_router, prefix="/api/v1/jobs", tags=["Jobs"])

@app.on_event("startup")
def on_startup():
    scheduler.start()

@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()
