from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from src.services.resume_service import parse_resumes_from_texts, parse_uploaded_bytes


router = APIRouter(prefix="/api/v1/resumes", tags=["resumes"])


@router.post("/parse-text")
def parse_text_resumes(resumes: list[str]):
    parsed = parse_resumes_from_texts(resumes)
    return {
        "count": len(parsed),
        "resumes": [item.model_dump() if hasattr(item, "model_dump") else item.__dict__ for item in parsed],
    }


@router.post("/upload")
async def upload_resumes(files: list[UploadFile] = File(...)):
    parsed_resumes = []
    for upload in files:
        file_bytes = await upload.read()
        parsed = parse_uploaded_bytes(upload.filename or "resume", file_bytes)
        parsed_resumes.append(parsed)

    return {
        "count": len(parsed_resumes),
        "resumes": [item.model_dump() if hasattr(item, "model_dump") else item.__dict__ for item in parsed_resumes],
    }
