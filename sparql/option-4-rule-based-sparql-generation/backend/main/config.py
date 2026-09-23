"""Configuration management for the DBLP exploration backend."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5.6-luna")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))

DBLP_SPARQL_ENDPOINT = os.getenv(
    "DBLP_SPARQL_ENDPOINT", "https://database-ir-anthology.srv.webis.de/"
)

EXAMPLES_PATH = BASE_DIR / os.getenv("EXAMPLES_PATH", "data/examples.json")

QUESTION_BATCH_SIZE = int(os.getenv("QUESTION_BATCH_SIZE", "10"))

ANALYTICS_DB_PATH = Path(
    os.getenv("ANALYTICS_DB_PATH", str(BASE_DIR / "data" / "analytics.sqlite3"))
)
_retention = os.getenv("ANALYTICS_RETENTION_DAYS", "")
ANALYTICS_RETENTION_DAYS = int(_retention) if _retention.strip() else None

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
