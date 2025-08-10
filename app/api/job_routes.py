from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.schemas.job_schema import JobRead, JobCreate, JobUpdate, JobRunResponse
from app.services import job_service
from app.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[JobRead])
def list_jobs(db: Session = Depends(get_db)):
    return job_service.get_all_jobs(db)

@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    return job_service.create_job(db, job_in)

@router.put("/{job_id}", response_model=JobRead)
def update_job(job_id: int, job_in: JobUpdate, db: Session = Depends(get_db)):
    job = job_service.update_job(db, job_id, job_in)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    success = job_service.delete_job(db, job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return

@router.post("/{job_id}/run", response_model=JobRunResponse)
def run_job(job_id: int, db: Session = Depends(get_db)):
    job = job_service.run_job_now(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobRunResponse(result=job.result, job_id=job_id)
