from datetime import datetime
from sqlalchemy.orm import Session
from app.models.job_model import Job
from app.schemas.job_schema import JobCreate, JobUpdate
from app.utils.scheduler import scheduler
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.base import BaseScheduler
import pytz

def print_first_10_primes():
    # The fake job: calculate and print first 10 primes
    primes = []
    num = 2
    while len(primes) < 10:
        if all(num % p != 0 for p in primes):
            primes.append(num)
        num += 1
    return primes

def get_job_result():
    primes = print_first_10_primes()
    return f"First 10 prime numbers: {primes}"

def schedule_job(job_id: int, interval: str, schedule_params: dict):
    # Remove existing APScheduler job for this job_id
    try:
        scheduler.remove_job(str(job_id))
    except JobLookupError:
        pass

    def job_func():
        from app.database import SessionLocal
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            result = get_job_result()
            utc_now = datetime.utcnow()
            ist = pytz.timezone('Asia/Kolkata')
            job.last_run_at = utc_now.replace(tzinfo=pytz.utc).astimezone(ist)
            job.result = result
            job.status = "completed"
            db.commit()
        db.close()
    
    # Scheduling
    job_instance = None
    if interval == "cron":
        job_instance = scheduler.add_job(
            job_func,
            trigger="cron",
            id=str(job_id),
            **schedule_params
        )
    elif interval == "interval":
        job_instance = scheduler.add_job(
            job_func,
            trigger="interval",
            id=str(job_id),
            **schedule_params
        )
    elif interval == "once":
        job_instance = scheduler.add_job(
            job_func,
            trigger="date",
            id=str(job_id),
            **schedule_params
        )
    # Update next_run_at in DB
    if job_instance:
        from app.database import SessionLocal
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            if job_instance.next_run_time:
                ist = pytz.timezone('Asia/Kolkata')
                job.next_run_at = job_instance.next_run_time.astimezone(ist)
            else:
                job.next_run_at = None
            db.commit()
        db.close()

def create_job(db: Session, job_in: JobCreate):
    import json
    job = Job(
        name=job_in.name,
        description=job_in.description,
        interval=job_in.interval,
        schedule_params=json.dumps(job_in.schedule_params) if job_in.schedule_params else None,
        status="scheduled"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    # Schedule if interval provided
    if job_in.interval and job_in.schedule_params:
        schedule_job(job.id, job_in.interval, job_in.schedule_params)
    return job

def get_all_jobs(db: Session):
    return db.query(Job).all()

def get_job(db: Session, job_id: int):
    return db.query(Job).filter(Job.id == job_id).first()

def update_job(db: Session, job_id: int, job_in: JobUpdate):
    import json
    job = get_job(db, job_id)
    if not job:
        return None
    for field, value in job_in.dict(exclude_unset=True).items():
        if field == "schedule_params" and value is not None:
            value = json.dumps(value)
        setattr(job, field, value)
    job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    # Update schedule
    if job_in.interval and job_in.schedule_params:
        schedule_job(job.id, job_in.interval, job_in.schedule_params)
    return job

def delete_job(db: Session, job_id: int):
    job = get_job(db, job_id)
    if not job:
        return False
    db.delete(job)
    db.commit()
    try:
        scheduler.remove_job(str(job_id))
    except JobLookupError:
        pass
    return True

def run_job_now(db: Session, job_id: int):
    job = get_job(db, job_id)
    if not job:
        return None
    result = get_job_result()
    utc_now = datetime.utcnow()
    ist = pytz.timezone('Asia/Kolkata')
    job.last_run_at = utc_now.replace(tzinfo=pytz.utc).astimezone(ist)
    job.result = result
    job.status = "completed"
    db.commit()
    db.refresh(job)
    return job
