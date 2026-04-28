# Resume Parser and Job Matcher

End-to-end MVP for resume parsing and job matching with:

- PDF/DOCX/TXT extraction
- resume and job description parsing
- semantic matching with Sentence-Transformers when available
- TF-IDF fallback for offline or blocked environments
- Streamlit dashboard
- FastAPI demo endpoint

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit app:

```bash
streamlit run src/app.py
```

Run the API:

```bash
uvicorn src.api:app --reload
```

Run the CLI demo:

```bash
python -m src.cli --demo
```

## Notes

- If Sentence-Transformers cannot load a model, the matcher falls back to TF-IDF.
- The demo mode works without any uploaded files.
