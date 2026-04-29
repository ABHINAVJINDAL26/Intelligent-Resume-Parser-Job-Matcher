from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.demo_data import get_demo_job_description, get_demo_resumes
from src.matcher import rank_resumes, results_to_records
from src.parser import parse_text_document
from src.routers.health import router as health_router
from src.routers.insights import router as insights_router
from src.routers.jobs import router as jobs_router
from src.routers.match import router as match_router
from src.routers.resumes import router as resumes_router
from src.schemas import MatchRequest


app = FastAPI(
    title="Resume Parser and Job Matcher",
    version="1.1.0",
    description="Layered FastAPI backend for resume parsing, matching, and insights.",
)

app.include_router(health_router)
app.include_router(resumes_router)
app.include_router(jobs_router)
app.include_router(match_router)
app.include_router(insights_router)


@app.post("/match")
def match_resumes_legacy(payload: MatchRequest):
    resume_docs = [parse_text_document(text, f"resume_{index + 1}") for index, text in enumerate(payload.resumes)]
    results = rank_resumes(resume_docs, payload.job_description, top_k=payload.top_k)
    return {"results": results_to_records(results)}


@app.get("/demo")
def demo_match(top_k: int = 5):
    demo_resumes = [parse_text_document(item["text"], item["file_name"]) for item in get_demo_resumes()]
    results = rank_resumes(demo_resumes, get_demo_job_description(), top_k=top_k)
    return {"results": results_to_records(results)}
