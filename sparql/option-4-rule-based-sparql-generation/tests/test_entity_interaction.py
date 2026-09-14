from backend.main.schemas.context import ExplorationContext, QueryResult
from backend.main.schemas.requests import EntityInteraction
from backend.main.schemas.responses import ResultColumn
from backend.main.services.sparql_generation import SPARQLGenerationService


class CapturingLLM:
    def __init__(self):
        self.user_prompt = ""

    def generate_structured(self, *, system_prompt, user_prompt, response_model):
        self.user_prompt = user_prompt
        return response_model(query="SELECT ?title WHERE { ?pub <https://dblp.org/rdf/schema#title> ?title . }")


def test_sparql_generation_receives_selected_entity_context():
    llm = CapturingLLM()
    service = SPARQLGenerationService(llm=llm)
    context = ExplorationContext(
        user_message="Show this author's publications",
        interaction=EntityInteraction(
            entity_id="https://dblp.org/pid/10/3248",
            entity_type="author",
        ),
    )

    result = service.run(context)

    assert result is not None
    assert "https://dblp.org/pid/10/3248" in llm.user_prompt
    assert "Do not resolve it from a name" in llm.user_prompt
    assert "using entity names" not in llm.user_prompt.split("SELECTED ENTITY CONTEXT:", 1)[-1]
