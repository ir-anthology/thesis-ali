"""FastAPI application entry point."""

from __future__ import annotations

import logging
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.main.api.exploration import router as exploration_router
from backend.main.api.health import router as health_router
from backend.main.config import API_HOST, API_PORT

RELOAD = os.getenv("RELOAD", "false").lower() == "true"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DBLP Exploration API",
    description="Conversational API for exploring the DBLP Computer Science Bibliography",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exploration_router)
app.include_router(health_router)


def run() -> None:
    """Run the FastAPI application."""
    uvicorn.run(
        "backend.main.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=RELOAD,
    )


if __name__ == "__main__":
    run()
