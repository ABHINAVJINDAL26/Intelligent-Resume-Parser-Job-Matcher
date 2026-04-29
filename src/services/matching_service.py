from __future__ import annotations

from src.matcher import MatchResult, explain_result, rank_resumes, results_to_records
from src.parser import ParsedDocument


def match_resumes(resume_docs: list[ParsedDocument], job_description: str, top_k: int = 5) -> list[MatchResult]:
    return rank_resumes(resume_docs, job_description, top_k=top_k)


def explain_matches(results: list[MatchResult]) -> list[str]:
    return [explain_result(result) for result in results]


def serialize_results(results: list[MatchResult]) -> list[dict]:
    return results_to_records(results)
