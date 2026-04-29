from __future__ import annotations

from fastapi import APIRouter

from src.demo_data import get_demo_job_description


router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.get("/demo")
def demo_job_description() -> dict:
    return {"job_description": get_demo_job_description()}
