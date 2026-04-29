from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from src.parser import ParsedDocument, parse_document, parse_text_document


def parse_resumes_from_texts(resume_texts: list[str]) -> list[ParsedDocument]:
    return [parse_text_document(text, f"resume_{index + 1}") for index, text in enumerate(resume_texts)]


def parse_resume_file(file_path: str | Path) -> ParsedDocument:
    return parse_document(file_path)


def parse_uploaded_bytes(file_name: str, file_bytes: bytes) -> ParsedDocument:
    suffix = Path(file_name).suffix.lower()
    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(file_bytes)
        temp_path = Path(temp_file.name)
    try:
        parsed = parse_document(temp_path)
        parsed.file_name = file_name
        return parsed
    finally:
        temp_path.unlink(missing_ok=True)
