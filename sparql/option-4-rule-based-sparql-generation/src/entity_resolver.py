"""Step 2: Entity resolution using DBLP Search API with caching."""

import json
import logging
import time
from pathlib import Path
import httpx
from .config import (
    DBLP_AUTHOR_API,
    DBLP_VENUE_API,
    DBLP_SEARCH_API,
    ENTITY_CACHE_PATH,
    DBLP_API_DELAY,
    KNOWN_PERSON_URIS,
    KNOWN_VENUE_URIS,
)
from .models import EntityMention, ResolvedEntity, EntityResolutionResult, Candidate

logger = logging.getLogger(__name__)


class EntityResolver:
    """Resolves entity mentions to DBLP URIs using Search API."""

    def __init__(self):
        self.client = httpx.Client(timeout=10.0)
        self.cache = self._load_cache()
        self._last_api_call = 0.0

    def _load_cache(self) -> dict:
        """Load entity cache from file."""
        if ENTITY_CACHE_PATH.exists():
            try:
                with open(ENTITY_CACHE_PATH) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning("Could not load entity cache: %s", str(e))
        return {}

    def _save_cache(self):
        """Save entity cache to file."""
        try:
            ENTITY_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(ENTITY_CACHE_PATH, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.warning("Could not save entity cache: %s", str(e))

    def _rate_limit(self):
        """Enrate rate limiting between API calls."""
        elapsed = time.time() - self._last_api_call
        if elapsed < DBLP_API_DELAY:
            time.sleep(DBLP_API_DELAY - elapsed)
        self._last_api_call = time.time()

    def resolve(self, mention: EntityMention) -> ResolvedEntity:
        """Resolve a single entity mention to a DBLP URI.

        Args:
            mention: Entity mention with text and type hint

        Returns:
            ResolvedEntity with URI, confidence, and status
        """
        text = mention.text.strip()
        text_lower = text.lower()

        logger.info("Resolving entity: %s (type_hint: %s)", text, mention.type_hint)

        # Check cache first
        if text_lower in self.cache:
            cached = self.cache[text_lower]
            logger.info("Found in cache: %s", cached.get("uri"))
            return ResolvedEntity(
                mention=text,
                uri=cached.get("uri"),
                label=cached.get("label", text),
                type=cached.get("type"),
                confidence=cached.get("confidence", 1.0),
            )

        # Check known URIs
        if mention.type_hint == "Person" or text_lower in KNOWN_PERSON_URIS:
            if text_lower in KNOWN_PERSON_URIS:
                uri = KNOWN_PERSON_URIS[text_lower]
                self._cache_entity(text, uri, "Person", 1.0)
                return ResolvedEntity(
                    mention=text, uri=uri, label=text, type="Person", confidence=1.0
                )
            return self._resolve_person(text)

        if (
            mention.type_hint in ("Conference", "Journal", "Venue")
            or text_lower in KNOWN_VENUE_URIS
        ):
            if text_lower in KNOWN_VENUE_URIS:
                uri = KNOWN_VENUE_URIS[text_lower]
                venue_type = "Conference" if "/conf/" in uri else "Journal"
                self._cache_entity(text, uri, venue_type, 1.0)
                return ResolvedEntity(
                    mention=text, uri=uri, label=text, type=venue_type, confidence=1.0
                )
            return self._resolve_venue(text, mention.type_hint)

        # Default: try author search first, then venue
        result = self._resolve_person(text)
        if result.uri:
            return result

        return self._resolve_venue(text, "Venue")

    def _resolve_person(self, name: str) -> ResolvedEntity:
        """Resolve a person name to DBLP person URI."""
        self._rate_limit()

        try:
            params = {"q": name, "format": "json", "h": 5}
            response = self.client.get(DBLP_AUTHOR_API, params=params)
            response.raise_for_status()
            data = response.json()

            hits = data.get("result", {}).get("hits", {}).get("hit", [])
            if isinstance(hits, dict):
                hits = [hits]

            if not hits:
                logger.info("No author found for: %s", name)
                return ResolvedEntity(mention=name, not_found=True, confidence=0.0)

            if len(hits) == 1:
                hit = hits[0]
                author_info = hit.get("info", {})
                uri = author_info.get("author-url", "")
                label = author_info.get("author", name)
                if uri:
                    self._cache_entity(name, uri, "Person", 0.9)
                    return ResolvedEntity(
                        mention=name,
                        uri=uri,
                        label=label,
                        type="Person",
                        confidence=0.9,
                    )

            # Multiple matches - ambiguous
            candidates = []
            for hit in hits[:3]:
                info = hit.get("info", {})
                candidates.append(
                    Candidate(
                        uri=info.get("author-url", ""),
                        label=info.get("author", ""),
                    )
                )

            logger.info("Ambiguous author: %s, %d candidates", name, len(candidates))
            return ResolvedEntity(
                mention=name,
                ambiguous=True,
                candidates=candidates,
                confidence=0.5,
            )

        except Exception as e:
            logger.error("Author search failed for %s: %s", name, str(e))
            return ResolvedEntity(mention=name, not_found=True, confidence=0.0)

    def _resolve_venue(self, name: str, hint: str) -> ResolvedEntity:
        """Resolve a venue name to DBLP venue URI."""
        self._rate_limit()

        try:
            params = {"q": name, "format": "json", "h": 5}
            response = self.client.get(DBLP_VENUE_API, params=params)
            response.raise_for_status()
            data = response.json()

            hits = data.get("result", {}).get("hits", {}).get("hit", [])
            if isinstance(hits, dict):
                hits = [hits]

            if not hits:
                logger.info("No venue found for: %s", name)
                return ResolvedEntity(mention=name, not_found=True, confidence=0.0)

            if len(hits) == 1:
                hit = hits[0]
                venue_info = hit.get("info", {})
                uri = venue_info.get("url", "")
                label = venue_info.get("venue", name)
                if uri:
                    venue_type = "Conference" if "/conf/" in uri else "Journal"
                    self._cache_entity(name, uri, venue_type, 0.9)
                    return ResolvedEntity(
                        mention=name,
                        uri=uri,
                        label=label,
                        type=venue_type,
                        confidence=0.9,
                    )

            # Multiple matches - ambiguous
            candidates = []
            for hit in hits[:3]:
                info = hit.get("info", {})
                candidates.append(
                    Candidate(
                        uri=info.get("url", ""),
                        label=info.get("venue", ""),
                    )
                )

            logger.info("Ambiguous venue: %s, %d candidates", name, len(candidates))
            return ResolvedEntity(
                mention=name,
                ambiguous=True,
                candidates=candidates,
                confidence=0.5,
            )

        except Exception as e:
            logger.error("Venue search failed for %s: %s", name, str(e))
            return ResolvedEntity(mention=name, not_found=True, confidence=0.0)

    def _cache_entity(
        self, mention: str, uri: str, entity_type: str, confidence: float
    ):
        """Cache an entity mapping."""
        self.cache[mention.lower().strip()] = {
            "uri": uri,
            "type": entity_type,
            "label": mention,
            "confidence": confidence,
        }
        self._save_cache()

    def resolve_batch(self, mentions: list[EntityMention]) -> EntityResolutionResult:
        """Resolve multiple entity mentions.

        Args:
            mentions: List of entity mentions to resolve

        Returns:
            EntityResolutionResult with resolved entities and unresolved mentions
        """
        resolved = []
        unresolved = []

        for mention in mentions:
            result = self.resolve(mention)
            resolved.append(result)
            if result.not_found:
                unresolved.append(mention.text)

        return EntityResolutionResult(
            resolved_entities=resolved,
            unresolved_mentions=unresolved,
        )

    def close(self):
        """Close the HTTP client."""
        self.client.close()
