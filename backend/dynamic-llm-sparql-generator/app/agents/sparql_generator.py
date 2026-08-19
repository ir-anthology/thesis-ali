import os

import httpx

TEXT2SPARQL_API_URL = os.environ.get("TEXT2SPARQL_API_URL", "http://localhost:8080")
TIMEOUT_SECONDS = 30


def execute(request: str) -> str:
    response = httpx.post(
        f"{TEXT2SPARQL_API_URL}/api/v1/query",
        json={"question": request, "execute": False},
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()
    return data["sparql"]
