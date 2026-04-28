from __future__ import annotations

import argparse
from pathlib import Path

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.demo_data import get_demo_job_description, get_demo_resumes
from src.matcher import rank_resumes, results_to_records
from src.parser import parse_document, parse_text_document


def run_demo(top_k: int) -> None:
    resumes = [parse_text_document(item["text"], item["file_name"]) for item in get_demo_resumes()]
    results = rank_resumes(resumes, get_demo_job_description(), top_k=top_k)
    for record in results_to_records(results):
        print(record)


def run_folder(resume_folder: Path, job_text_path: Path, top_k: int) -> None:
    job_text = job_text_path.read_text(encoding="utf-8")
    resume_docs = []
    for path in sorted(resume_folder.iterdir()):
        if path.suffix.lower() in {".pdf", ".docx", ".doc", ".txt", ".md"}:
            resume_docs.append(parse_document(path))
    results = rank_resumes(resume_docs, job_text, top_k=top_k)
    for record in results_to_records(results):
        print(record)


def main() -> None:
    parser = argparse.ArgumentParser(description="Resume parser and job matcher")
    parser.add_argument("--demo", action="store_true", help="Run with built-in demo data")
    parser.add_argument("--resume-folder", type=Path, help="Folder containing resume files")
    parser.add_argument("--job-text", type=Path, help="Text file containing the job description")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    if args.demo or not args.resume_folder or not args.job_text:
        run_demo(args.top_k)
    else:
        run_folder(args.resume_folder, args.job_text, args.top_k)


if __name__ == "__main__":
    main()
