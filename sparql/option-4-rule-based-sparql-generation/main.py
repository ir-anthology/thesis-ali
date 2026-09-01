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

                # Output as raw JSON
                print(json.dumps(result.model_dump(), indent=2))

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
