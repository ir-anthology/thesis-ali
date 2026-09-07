"""FastAPI application for DBLP exploration."""

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import API_HOST, API_PORT
from .models import ChatRequest, ExplorationResponse
from .pipeline import Pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DBLP Exploration API",
    description="API for exploring the DBLP Computer Science Bibliography using natural language",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = Pipeline()


@app.post("/api/exploration", response_model=ExplorationResponse)
async def explore(request: ChatRequest) -> ExplorationResponse:
    """Process exploration query.

    Args:
        request: ChatRequest with message and conversation history

        Returns:
            ExplorationResponse with interpretation, columns, rows, observations, suggestions
    """
    logger.info("Received exploration request: %s", request.message)

    try:
        result = pipeline.explore(request.message, request.history)
        return result
    except Exception as e:
        logger.error("Pipeline failed: %s", str(e))
        return ExplorationResponse(
            interpretation=f"An error occurred while processing your query: {str(e)}",
            suggestions=[
                "Try rephrasing your question",
                "Ask about authors, publications, or venues",
                "Check if the entity names are correct",
            ],
        )


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


def run():
    """Run the FastAPI application."""
    uvicorn.run(
        "src.api:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
    )


if __name__ == "__main__":
    run()
