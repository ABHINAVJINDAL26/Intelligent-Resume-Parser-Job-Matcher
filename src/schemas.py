from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class MatchRequest:
    job_description: str
    resumes: list[str] = field(default_factory=list)
    top_k: int = 5


@dataclass(slots=True)
class TextParseRequest:
    file_name: str = "text_input"
    text: str = ""
