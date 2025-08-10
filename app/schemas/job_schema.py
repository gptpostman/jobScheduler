from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, root_validator

class JobBase(BaseModel):
    name: str
    description: Optional[str] = None
    interval: Optional[str] = Field(None, description="Job type: cron/interval/once")
    schedule_params: Optional[Dict[str, Any]] = Field(
        None, description="Schedule parameters (e.g. {'day_of_week': 'mon', ...})"
    )

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    interval: Optional[str] = None
    schedule_params: Optional[Dict[str, Any]] = None

class JobRead(JobBase):
    id: int
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    result: Optional[str]
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

    @root_validator(pre=True)
    def decode_schedule_params(cls, values):
        if isinstance(values, dict):
            val = values.get("schedule_params")
        else:
            val = getattr(values, "schedule_params", None)
        if isinstance(val, str):
            import json
            try:
                # If values is not a dict, convert to dict for assignment
                if not isinstance(values, dict):
                    values = dict(values.__dict__)
                values["schedule_params"] = json.loads(val)
            except Exception:
                values["schedule_params"] = None
        return values

class JobRunResponse(BaseModel):
    result: str
    job_id: int
