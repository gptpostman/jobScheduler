from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    interval = Column(String, nullable=True)  # e.g., "cron", "interval", "once"
    schedule_params = Column(String, nullable=True)  # e.g., {"day_of_week": "mon", ...} as JSON
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    result = Column(Text, nullable=True)
    status = Column(String, default="scheduled")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
