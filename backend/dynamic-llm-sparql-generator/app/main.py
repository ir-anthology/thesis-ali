from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents import router, sparql_executor, sparql_generator, table_formatter
from app.schemas import ChatRequest, ChatResponse

app = FastAPI(title="Conversational Knowledge Graph Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if router.is_sparql(request.message):
        results = sparql_executor.execute(request.message)

        if "error" in results:
            return ChatResponse(type="error", content=results["error"])

        table = table_formatter.format(results)
        return ChatResponse(type="table", content=table)
    else:
        sparql = sparql_generator.execute(request.message)
        return ChatResponse(type="sparql", content=sparql)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
