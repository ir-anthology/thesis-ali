"""Step 3: Rule-based limitation detection for DBLP queries."""

import logging
from .config import LIMITATION_KEYWORDS
from .models import IntentResult, LimitationResult

logger = logging.getLogger(__name__)


class LimitationDetector:
    """Detects if a query requires features not available in DBLP."""

    def detect(self, user_query: str, intent_result: IntentResult) -> LimitationResult:
        """Detect if the query has limitations based on DBLP capabilities.

        Args:
            user_query: Original natural language query
            intent_result: Result from intent classification

        Returns:
            LimitationResult with limitation status and message
        """
        logger.info("Checking limitations for query: %s", user_query)

        query_lower = user_query.lower()

        # Check for limitation keywords
        for keyword, message in LIMITATION_KEYWORDS.items():
            if keyword in query_lower:
                logger.info("Limitation detected: %s", keyword)
                return LimitationResult(has_limitation=True, limitation=message)

        # Check for specific intent-based limitations
        if intent_result.intent.value == "unknown":
            # Check if query is about non-CS topics
            non_cs_keywords = [
                "biology",
                "chemistry",
                "physics",
                "medicine",
                "history",
                "literature",
                "philosophy",
                "economics",
                "psychology",
                "sociology",
            ]
            for keyword in non_cs_keywords:
                if keyword in query_lower:
                    logger.info("Non-CS topic detected: %s", keyword)
                    return LimitationResult(
                        has_limitation=True,
                        limitation=f"DBLP focuses on computer science publications only. Information about {keyword} is not available in DBLP.",
                    )

        logger.info("No limitations detected")
        return LimitationResult(has_limitation=False, limitation=None)
