import httpx

DBLP_SPARQL_ENDPOINT = "https://sparql.dblp.org/sparql"
TIMEOUT_SECONDS = 30


def execute(sparql: str) -> dict:
    try:
        response = httpx.post(
            DBLP_SPARQL_ENDPOINT,
            data={"query": sparql},
            headers={"Accept": "application/sparql-results+json"},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        return {"error": "SPARQL query timed out"}
    except httpx.HTTPStatusError as e:
        return {"error": f"SPARQL endpoint returned {e.response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
