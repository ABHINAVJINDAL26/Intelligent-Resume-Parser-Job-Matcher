from __future__ import annotations

from src.sample_data import DEMO_JOB_DESCRIPTION, DEMO_RESUMES


def get_demo_job_description() -> str:
    return DEMO_JOB_DESCRIPTION


def get_demo_resumes() -> list[dict]:
    return DEMO_RESUMES
