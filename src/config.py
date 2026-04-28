from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
MODELS_DIR = PROJECT_ROOT / "models"

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_TOP_K = 5
DEFAULT_RESUME_SCORE_WEIGHT = 0.6
DEFAULT_SKILL_SCORE_WEIGHT = 0.3
DEFAULT_EXPERIENCE_SCORE_WEIGHT = 0.1

COMMON_SKILLS = [
    "python",
    "java",
    "sql",
    "excel",
    "power bi",
    "tableau",
    "pandas",
    "numpy",
    "scikit learn",
    "sklearn",
    "tensorflow",
    "pytorch",
    "nlp",
    "machine learning",
    "deep learning",
    "data analysis",
    "data science",
    "fastapi",
    "streamlit",
    "docker",
    "aws",
    "gcp",
    "faiss",
    "redis",
    "mongodb",
    "postgresql",
    "git",
    "linux",
    "communication",
    "leadership",
]
