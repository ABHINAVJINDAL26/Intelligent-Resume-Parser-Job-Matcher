from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile

from src.schemas import MatchRequest
from src.services.matching_service import match_resumes, serialize_results
from src.services.resume_service import parse_resumes_from_texts, parse_uploaded_bytes


router = APIRouter(prefix="/api/v1/match", tags=["matching"])


@router.post("")
def match(payload: MatchRequest) -> dict:
    resume_docs = parse_resumes_from_texts(payload.resumes)
    results = match_resumes(resume_docs, payload.job_description, top_k=payload.top_k)
    return {"results": serialize_results(results)}


@router.post("/upload")
async def match_uploaded(
    job_description: str = Form(...),
    files: list[UploadFile] = File(...),
    top_k: int = Form(5),
) -> dict:
    resume_docs = []
    for upload in files:
        file_bytes = await upload.read()
        parsed = parse_uploaded_bytes(upload.filename or "resume", file_bytes)
        parsed.file_name = Path(upload.filename or parsed.file_name).name
        resume_docs.append(parsed)

    results = match_resumes(resume_docs, job_description, top_k=top_k)
    return {"results": serialize_results(results)}
