# Resume Parser and Job Matcher

This repo now has two layers:

- the working Streamlit MVP for fast local validation
- a production-style FastAPI + React scaffold that follows the architecture diagram

## What is working now

- PDF/DOCX/TXT extraction
- resume and job description parsing
- semantic matching with Sentence-Transformers when available
- TF-IDF fallback for offline or blocked environments
- Streamlit dashboard
- FastAPI layered routers for health, resumes, jobs, matching, and insights
- React frontend scaffold with upload/demo flows

## Run the MVP

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

## Run the frontend scaffold

```bash
cd frontend
npm install
npm run dev
```

The frontend proxies API calls to `http://127.0.0.1:8000`.

## Run everything with npm

Install root dependencies once:

```bash
npm install
```

Start backend and frontend together from the project root:

```bash
npm run start:all
```

Available npm scripts:

- `npm run start:backend` starts FastAPI on port `8000`
- `npm run start:frontend` starts Vite on port `5173`
- `npm run start:mvp` starts the Streamlit app on port `8501`

## API routes

- `GET /health`
- `POST /match`
- `POST /api/v1/match/upload`
- `GET /api/v1/jobs/demo`
- `POST /api/v1/resumes/upload`
- `POST /api/v1/insights/match-summary`

## Notes

- If Sentence-Transformers cannot load a model, the matcher falls back to TF-IDF.
- The demo mode works without any uploaded files.
