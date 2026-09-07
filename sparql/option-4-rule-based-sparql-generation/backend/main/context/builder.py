"""Context builder — constructs an ExplorationContext from a ChatRequest."""

from __future__ import annotations

from backend.main.schemas.requests import ChatRequest
from backend.main.schemas.context import ExplorationContext
from backend.main.schema.provider import DBLPSchemaProvider


class ContextBuilder:
    """Builds the initial ExplorationContext from a frontend request."""

    def __init__(self, schema_provider: DBLPSchemaProvider | None = None) -> None:
        self._schema = schema_provider or DBLPSchemaProvider()

    def build(self, request: ChatRequest) -> ExplorationContext:
        """Create the initial context (C0) from a ChatRequest.

        The context is progressively enriched by subsequent pipeline stages.
        """
        ctx = ExplorationContext(
            user_message=request.message,
            history=request.history,
        )
        ctx.set_schema(self._schema.get_schema())
        return ctx
