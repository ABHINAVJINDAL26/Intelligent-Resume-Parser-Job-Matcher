from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.demo_data import get_demo_job_description, get_demo_resumes
from src.matcher import rank_resumes, results_to_records
from src.parser import parse_text_document


app = FastAPI(title="Resume Parser and Job Matcher", version="1.0.0")


class MatchRequest(BaseModel):
    job_description: str
    resumes: list[str] = Field(default_factory=list)
    top_k: int = 5


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/match")
def match_resumes(payload: MatchRequest):
    resume_docs = [parse_text_document(text, f"resume_{index + 1}") for index, text in enumerate(payload.resumes)]
    results = rank_resumes(resume_docs, payload.job_description, top_k=payload.top_k)
    return {"results": results_to_records(results)}


@app.get("/demo")
def demo_match(top_k: int = 5):
    demo_resumes = [parse_text_document(item["text"], item["file_name"]) for item in get_demo_resumes()]
    results = rank_resumes(demo_resumes, get_demo_job_description(), top_k=top_k)
    return {"results": results_to_records(results)}
