from __future__ import annotations

from fastapi import APIRouter

from src.matcher import explain_result
from src.schemas import MatchRequest
from src.services.matching_service import match_resumes
from src.services.resume_service import parse_resumes_from_texts


router = APIRouter(prefix="/api/v1/insights", tags=["insights"])


@router.post("/match-summary")
def match_summary(payload: MatchRequest) -> dict:
    resume_docs = parse_resumes_from_texts(payload.resumes)
    results = match_resumes(resume_docs, payload.job_description, top_k=payload.top_k)
    return {"summary": [explain_result(result) for result in results]}
