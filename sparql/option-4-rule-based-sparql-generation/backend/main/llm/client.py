"""Centralised LLM client abstraction.

Individual services call ``LLMClient.generate_structured()`` instead of using
the OpenAI SDK directly.  This isolates provider-specific code.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

from backend.main.config import (
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_TEMPERATURE,
    OPENAI_API_KEY,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """Reusable LLM client with structured-output support."""

    def __init__(self) -> None:
        self._client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = LLM_MODEL
        self.temperature = LLM_TEMPERATURE
        self.max_tokens = LLM_MAX_TOKENS

    # ------------------------------------------------------------------
    # Structured output via Responses API
    # ------------------------------------------------------------------

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T | None:
        """Call the LLM and parse the response into *response_model*.

        Uses the OpenAI Responses API with structured outputs.

        Returns ``None`` when the LLM returns nothing or parsing fails.
        """
        try:
            response = self._client.responses.parse(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                text_format=response_model,
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
            result = response.output_parsed
            if result is None:
                logger.warning("LLM returned None for %s", response_model.__name__)
            return result
        except Exception:
            logger.exception("LLM call failed for %s", response_model.__name__)
            return None

    # ------------------------------------------------------------------
    # Plain JSON output via Chat Completions API
    # ------------------------------------------------------------------

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict | None:
        """Call the LLM and return parsed JSON.

        Uses the Chat Completions API with ``response_format={"type": "json_object"}``.
        """
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            content = response.choices[0].message.content
            if not content:
                logger.warning("LLM returned empty content")
                return None
            return json.loads(content)
        except Exception:
            logger.exception("LLM JSON call failed")
            return None


def load_prompt(name: str) -> str:
    """Load a prompt text file from ``llm/prompts/``.

    Args:
        name: Filename without extension (e.g. ``"interpretation"``).
    """
    path = Path(__file__).resolve().parent / "prompts" / f"{name}.txt"
    return path.read_text(encoding="utf-8")
