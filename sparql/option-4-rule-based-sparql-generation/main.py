"""CLI entry point for rule-based SPARQL generation."""

import sys
import json
import logging
from src.pipeline import Pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Run the SPARQL generation pipeline interactively."""
    print("=" * 60)
    print("DBLP Text-to-SPARQL (Rule-Based)")
    print("=" * 60)
    print("Type your question about DBLP publications.")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    pipeline = Pipeline()

    try:
        while True:
            try:
                user_input = input("\nQuestion: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ("quit", "exit", "q"):
                    print("Goodbye!")
                    break

                result = pipeline.convert(user_input)

                print("\n" + "-" * 40)
                print(f"Intent: {result.intent}")

                if result.limitation:
                    print(f"\nLimitation: {result.limitation}")

                if result.clarification:
                    print(f"\nClarification: {result.clarification}")

                if result.sparql_query:
                    print(f"\nSPARQL Query:\n{result.sparql_query}")

                if result.suggestions:
                    print("\nSuggestions:")
                    for i, suggestion in enumerate(result.suggestions, 1):
                        print(f"  {i}. {suggestion}")

                print("-" * 40)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error("Error processing query: %s", str(e))
                print(f"\nError: {str(e)}")

    finally:
        pipeline.close()


def run_single_query(query: str):
    """Run a single query and return the result as JSON.

    Args:
        query: Natural language question about DBLP

    Returns:
        JSON string with the result
    """
    pipeline = Pipeline()

    try:
        result = pipeline.convert(query)
        return json.dumps(result.model_dump(), indent=2)
    finally:
        pipeline.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(run_single_query(query))
    else:
        main()
