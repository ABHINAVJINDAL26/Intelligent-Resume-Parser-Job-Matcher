from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EXPERIENCE_SCORE_WEIGHT,
    DEFAULT_RESUME_SCORE_WEIGHT,
    DEFAULT_SKILL_SCORE_WEIGHT,
    DEFAULT_TOP_K,
)
from src.parser import ParsedDocument, extract_skills, parse_text_document

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None


@dataclass
class MatchResult:
    file_name: str
    candidate_name: str
    score: float
    semantic_score: float
    skill_score: float
    experience_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    experience_years: float | None
    method: str


class SemanticScorer:
    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        self.model_name = model_name
        self._model = None
        self._tfidf = None
        self._fallback_mode = False

    def _load_model(self):
        if self._model is not None or self._fallback_mode:
            return self._model

        if SentenceTransformer is None:
            self._fallback_mode = True
            return None

        try:
            self._model = SentenceTransformer(self.model_name)
        except Exception:
            self._fallback_mode = True
            self._model = None
        return self._model

    def score(self, left_texts: Iterable[str], right_text: str) -> list[float]:
        left_list = list(left_texts)
        model = self._load_model()

        if model is not None:
            left_embeddings = model.encode(left_list, normalize_embeddings=True)
            right_embedding = model.encode([right_text], normalize_embeddings=True)
            scores = cosine_similarity(left_embeddings, right_embedding).reshape(-1)
            return [float(score) for score in scores]

        corpus = left_list + [right_text]
        self._tfidf = TfidfVectorizer(stop_words="english")
        matrix = self._tfidf.fit_transform(corpus)
        scores = cosine_similarity(matrix[:-1], matrix[-1:]).reshape(-1)
        return [float(score) for score in scores]


def _normalize_score(value: float) -> float:
    return max(0.0, min(1.0, value))


def _experience_score(candidate_years: float | None, required_years: float | None) -> float:
    if not required_years or required_years <= 0:
        return 1.0 if candidate_years is not None else 0.5
    if candidate_years is None:
        return 0.0
    return _normalize_score(min(candidate_years / required_years, 1.0))


def rank_resumes(
    resume_docs: list[ParsedDocument],
    job_text: str,
    top_k: int = DEFAULT_TOP_K,
    required_years: float | None = None,
) -> list[MatchResult]:
    if not resume_docs:
        return []

    job_doc = parse_text_document(job_text, file_name="job_description")
    job_skills = extract_skills(job_doc.normalized_text)
    if required_years is None:
        required_years = job_doc.experience_years

    scorer = SemanticScorer()
    semantic_scores = scorer.score([resume.normalized_text for resume in resume_docs], job_doc.normalized_text)

    results: list[MatchResult] = []
    for resume, semantic_score in zip(resume_docs, semantic_scores, strict=False):
        matched_skills = sorted(set(resume.skills).intersection(job_skills))
        missing_skills = [skill for skill in job_skills if skill not in matched_skills]
        skill_score = len(matched_skills) / max(len(job_skills), 1)
        experience_score = _experience_score(resume.experience_years, required_years)
        total_score = (
            semantic_score * DEFAULT_RESUME_SCORE_WEIGHT
            + skill_score * DEFAULT_SKILL_SCORE_WEIGHT
            + experience_score * DEFAULT_EXPERIENCE_SCORE_WEIGHT
        )

        results.append(
            MatchResult(
                file_name=resume.file_name,
                candidate_name=resume.candidate_name,
                score=round(_normalize_score(total_score), 4),
                semantic_score=round(_normalize_score(semantic_score), 4),
                skill_score=round(_normalize_score(skill_score), 4),
                experience_score=round(_normalize_score(experience_score), 4),
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                experience_years=resume.experience_years,
                method="sentence-transformers" if scorer._model is not None else "tfidf-fallback",
            )
        )

    results.sort(key=lambda item: item.score, reverse=True)
    return results[:top_k]


def explain_result(result: MatchResult) -> str:
    matched = ", ".join(result.matched_skills) if result.matched_skills else "none"
    missing = ", ".join(result.missing_skills[:5]) if result.missing_skills else "none"
    return (
        f"{result.candidate_name} matched {matched}. "
        f"Missing skills: {missing}. "
        f"Experience score: {result.experience_score:.2f}."
    )


def results_to_records(results: list[MatchResult]) -> list[dict]:
    return [asdict(result) for result in results]
