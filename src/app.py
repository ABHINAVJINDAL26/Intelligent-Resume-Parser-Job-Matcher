from __future__ import annotations

import zipfile
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pandas as pd
import streamlit as st

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.demo_data import get_demo_job_description, get_demo_resumes
from src.matcher import rank_resumes, results_to_records
from src.parser import parse_document, parse_text_document


st.set_page_config(page_title="Resume Matcher", page_icon="Resume Matcher", layout="wide")


st.markdown(
    """
<style>
    .block-container { padding-top: 2rem; }
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 45%, #111827 100%);
        color: white;
        padding: 1.5rem 1.75rem;
        border-radius: 20px;
        border: 1px solid rgba(148, 163, 184, 0.2);
        margin-bottom: 1rem;
    }
    .muted { color: #94a3b8; }
</style>
""",
    unsafe_allow_html=True,
)


st.markdown(
    """
<div class="hero">
  <h1 style="margin:0;">Intelligent Resume Parser & Job Matcher</h1>
  <p style="margin:0.4rem 0 0 0;" class="muted">Upload resumes, paste a job description, and get ranked matches with skill gaps.</p>
</div>
""",
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("Controls")
    use_demo = st.toggle("Use demo data", value=True)
    top_k = st.slider("Top candidates", 1, 10, 5)
    st.caption("Supported uploads: PDF, DOCX, TXT, ZIP")


job_description = st.text_area("Job description", value=get_demo_job_description(), height=200)
uploaded_files = st.file_uploader(
    "Upload resume files",
    type=["pdf", "docx", "txt", "md", "zip"],
    accept_multiple_files=True,
)


resume_docs = []
if use_demo and not uploaded_files:
    resume_docs = [parse_text_document(item["text"], item["file_name"]) for item in get_demo_resumes()]
    st.info("Demo data loaded. Turn off demo mode to upload your own resumes.")
elif uploaded_files:
    for upload in uploaded_files:
        upload_bytes = upload.getvalue()
        suffix = Path(upload.name).suffix.lower()

        if suffix == ".zip":
            with TemporaryDirectory() as temp_dir:
                archive_path = Path(temp_dir) / upload.name
                archive_path.write_bytes(upload_bytes)

                with zipfile.ZipFile(archive_path) as archive:
                    members = [item for item in archive.infolist() if not item.is_dir()]
                    for index, member in enumerate(members):
                        member_suffix = Path(member.filename).suffix.lower()
                        if member_suffix not in {".pdf", ".docx", ".txt", ".md"}:
                            continue

                        extracted_name = f"{index}_{Path(member.filename).name}"
                        extracted_path = Path(temp_dir) / extracted_name
                        extracted_path.write_bytes(archive.read(member))
                        parsed = parse_document(extracted_path)
                        parsed.file_name = f"{upload.name}:{member.filename}"
                        resume_docs.append(parsed)
        else:
            with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(upload_bytes)
                temp_path = Path(temp_file.name)
            try:
                resume_docs.append(parse_document(temp_path))
            finally:
                temp_path.unlink(missing_ok=True)


run_match = st.button("Run matching", type="primary", use_container_width=True)


if run_match:
    if not job_description.strip():
        st.error("Please enter a job description.")
        st.stop()

    if not resume_docs:
        st.error("Please upload at least one resume or enable demo mode.")
        st.stop()

    results = rank_resumes(resume_docs, job_description, top_k=top_k)
    records = results_to_records(results)
    frame = pd.DataFrame(records)

    col1, col2, col3 = st.columns(3)
    col1.metric("Resumes processed", len(resume_docs))
    col2.metric("Top match", frame.iloc[0]["candidate_name"] if not frame.empty else "N/A")
    col3.metric("Best score", f"{frame.iloc[0]['score']:.2f}" if not frame.empty else "0.00")

    st.subheader("Ranked results")
    display_frame = frame[["candidate_name", "score", "semantic_score", "skill_score", "experience_score", "matched_skills", "missing_skills"]].copy()
    st.dataframe(display_frame, use_container_width=True, hide_index=True)

    if not frame.empty:
        st.subheader("Skill gap view")
        selected = st.selectbox("Inspect candidate", frame["candidate_name"].tolist())
        selected_row = frame[frame["candidate_name"] == selected].iloc[0]
        gap_col1, gap_col2 = st.columns(2)
        gap_col1.write("Matched skills")
        gap_col1.write(", ".join(selected_row["matched_skills"]) or "None")
        gap_col2.write("Missing skills")
        gap_col2.write(", ".join(selected_row["missing_skills"]) or "None")

        export_csv = frame.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", export_csv, file_name="resume_matches.csv", mime="text/csv")

        try:
            export_xlsx = Path("resume_matches.xlsx")
            frame.to_excel(export_xlsx, index=False)
            with open(export_xlsx, "rb") as workbook_file:
                st.download_button(
                    "Download Excel",
                    workbook_file.read(),
                    file_name="resume_matches.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            export_xlsx.unlink(missing_ok=True)
        except Exception:
            st.caption("Excel export unavailable in this environment.")
