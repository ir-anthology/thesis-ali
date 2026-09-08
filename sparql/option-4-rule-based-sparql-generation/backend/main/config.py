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

MAX_RESULT_ROWS = int(os.getenv("MAX_RESULT_ROWS", "50"))
QUESTION_BATCH_SIZE = int(os.getenv("QUESTION_BATCH_SIZE", "10"))

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
