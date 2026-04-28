from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pdfplumber
import spacy
from langdetect import detect, LangDetectException

from src.config import COMMON_SKILLS

try:
    import docx2txt
except Exception:  # pragma: no cover - optional dependency
    docx2txt = None

try:
    from indic_transliteration.sanscript import DEVANAGARI, IAST, transliterate
except Exception:  # pragma: no cover - optional dependency
    DEVANAGARI = IAST = transliterate = None

try:
    import fitz
except Exception:  # pragma: no cover - optional dependency
    fitz = None


_NLP = None


@dataclass
class ParsedDocument:
    file_name: str
    raw_text: str
    normalized_text: str
    candidate_name: str
    skills: list[str]
    experience_years: float | None
    source_type: str


def _load_nlp():
    global _NLP
    if _NLP is None:
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def read_document(file_path: str | Path) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _read_pdf(path)
    if suffix == ".docx":
        return _read_docx(path)
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"Unsupported file type: {suffix or 'unknown'}")


def _read_pdf(path: Path) -> str:
    if fitz is not None:
        try:
            doc = fitz.open(path)
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            if text.strip():
                return text
        except Exception:
            pass

    with pdfplumber.open(path) as pdf:
        parts = []
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text:
                parts.append(page_text)
        return "\n".join(parts)


def _read_docx(path: Path) -> str:
    if docx2txt is None:
        raise RuntimeError("docx2txt is not installed")
    return docx2txt.process(str(path)) or ""


def normalize_text(text: str) -> str:
    cleaned = text.replace("\r", "\n")
    try:
        lang = detect(cleaned)
    except LangDetectException:
        lang = "en"

    if lang == "hi" and transliterate is not None:
        try:
            cleaned = transliterate(cleaned, DEVANAGARI, IAST)
        except Exception:
            pass

    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_candidate_name(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "Unknown"

    first_line = lines[0]
    first_line = first_line.split("|")[0].strip()
    first_line = re.sub(r"[^A-Za-z .'-]", "", first_line)
    tokens = [token for token in first_line.split() if token]
    if 1 <= len(tokens) <= 4:
        return first_line

    return "Unknown"


def extract_years_of_experience(text: str) -> float | None:
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
        r"(\d+(?:\.\d+)?)\s*yrs?",
        r"experience[:\s]+(\d+(?:\.\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    return None


def extract_skills(text: str, skill_catalog: Iterable[str] | None = None) -> list[str]:
    catalog = list(skill_catalog or COMMON_SKILLS)
    lowered = text.lower()
    found = []

    for skill in catalog:
        skill_pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(skill_pattern, lowered):
            found.append(skill)

    return sorted(dict.fromkeys(found))


def extract_sections(text: str) -> dict[str, str]:
    lower = text.lower()
    sections = {}

    markers = ["skills", "experience", "education", "summary"]
    for marker in markers:
        match = re.search(rf"(?:^|\n)\s*{marker}\s*[:\-]?\s*", lower)
        if match:
            start = match.end()
            next_positions = [
                lower.find(other, start)
                for other in markers
                if other != marker and lower.find(other, start) != -1
            ]
            end = min(next_positions) if next_positions else len(text)
            sections[marker] = text[start:end].strip()

    return sections


def parse_document(file_path: str | Path) -> ParsedDocument:
    raw_text = read_document(file_path)
    normalized = normalize_text(raw_text)
    source_type = Path(file_path).suffix.lower().lstrip(".") or "text"
    return ParsedDocument(
        file_name=Path(file_path).name,
        raw_text=raw_text,
        normalized_text=normalized,
        candidate_name=extract_candidate_name(normalized),
        skills=extract_skills(normalized),
        experience_years=extract_years_of_experience(normalized),
        source_type=source_type,
    )


def parse_text_document(text: str, file_name: str = "text_input") -> ParsedDocument:
    normalized = normalize_text(text)
    return ParsedDocument(
        file_name=file_name,
        raw_text=text,
        normalized_text=normalized,
        candidate_name=extract_candidate_name(normalized),
        skills=extract_skills(normalized),
        experience_years=extract_years_of_experience(normalized),
        source_type="text",
    )


def load_spacy_doc(text: str):
    nlp = _load_nlp()
    return nlp(text)
