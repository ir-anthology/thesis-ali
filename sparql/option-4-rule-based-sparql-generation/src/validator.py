"""Step 6: SPARQL query validation."""

import re
import logging
from .config import DBLP_KEY_PREDICATES, DBLP_KEY_CLASSES
from .models import ValidationResult

logger = logging.getLogger(__name__)


class SPARQLValidator:
    """Validates SPARQL queries for correctness."""

    def validate(self, sparql: str) -> ValidationResult:
        """Validate a SPARQL query.

        Args:
            sparql: SPARQL query string to validate

        Returns:
            ValidationResult with validity status, errors, and warnings
        """
        logger.info("Validating SPARQL query")

        if not sparql or not sparql.strip():
            return ValidationResult(
                valid=False, errors=["Empty SPARQL query"], warnings=[]
            )

        errors = []
        warnings = []

        # Check basic syntax
        syntax_errors = self._validate_syntax(sparql)
        errors.extend(syntax_errors)

        # Check prefixes
        prefix_errors = self._validate_prefixes(sparql)
        errors.extend(prefix_errors)

        # Check predicates
        pred_errors = self._validate_predicates(sparql)
        errors.extend(pred_errors)

        # Check classes
        class_errors = self._validate_classes(sparql)
        errors.extend(class_errors)

        # Check structure
        structure_warnings = self._validate_structure(sparql)
        warnings.extend(structure_warnings)

        valid = len(errors) == 0

        if valid:
            logger.info("SPARQL validation passed with %d warnings", len(warnings))
        else:
            logger.warning("SPARQL validation failed with %d errors", len(errors))

        return ValidationResult(valid=valid, errors=errors, warnings=warnings)

    def _validate_syntax(self, sparql: str) -> list[str]:
        """Validate basic SPARQL syntax."""
        errors = []

        # Check if query contains SELECT (may be after PREFIX declarations)
        sparql_upper = sparql.strip().upper()
        # Remove PREFIX declarations for SELECT check
        lines = sparql_upper.split("\n")
        non_prefix_lines = [l for l in lines if not l.strip().startswith("PREFIX")]
        query_body = "\n".join(non_prefix_lines).strip()

        if not query_body.startswith("SELECT"):
            errors.append("Query must start with SELECT")

        # Check for WHERE clause
        if "{" not in sparql or "}" not in sparql:
            errors.append("Missing WHERE clause braces")

        # Check balanced braces
        if sparql.count("{") != sparql.count("}"):
            errors.append("Unbalanced braces in query")

        return errors

    def _validate_prefixes(self, sparql: str) -> list[str]:
        """Validate prefix declarations."""
        errors = []

        # Check if dblp prefix is used but not declared
        if "dblp:" in sparql and "PREFIX dblp:" not in sparql:
            errors.append("Missing PREFIX declaration for dblp:")

        # Check if rdf prefix is used but not declared
        if "rdf:" in sparql and "PREFIX rdf:" not in sparql:
            errors.append("Missing PREFIX declaration for rdf:")

        # Check if xsd prefix is used but not declared
        if "xsd:" in sparql and "PREFIX xsd:" not in sparql:
            errors.append("Missing PREFIX declaration for xsd:")

        return errors

    def _validate_predicates(self, sparql: str) -> list[str]:
        """Validate predicates against known DBLP predicates."""
        errors = []
        known_predicates = set(DBLP_KEY_PREDICATES)

        # Extract predicates from query
        where_clause = self._extract_where_clause(sparql)
        if not where_clause:
            return errors

        # Find dblp: predicates
        pred_pattern = r"dblp:(\w+)"
        matches = re.findall(pred_pattern, where_clause)

        for pred in matches:
            if pred not in known_predicates:
                errors.append(f"Unknown predicate: dblp:{pred}")

        return errors

    def _validate_classes(self, sparql: str) -> list[str]:
        """Validate classes against known DBLP classes."""
        errors = []
        known_classes = set(DBLP_KEY_CLASSES)

        # Extract classes from query (after 'a' or 'rdf:type')
        where_clause = self._extract_where_clause(sparql)
        if not where_clause:
            return errors

        # Find class references after 'a' keyword
        type_pattern = r"\ba\s+dblp:(\w+)"
        matches = re.findall(type_pattern, where_clause)

        for cls in matches:
            if cls not in known_classes:
                errors.append(f"Unknown class: dblp:{cls}")

        return errors

    def _validate_structure(self, sparql: str) -> list[str]:
        """Validate query structure and return warnings."""
        warnings = []

        # Check for SELECT *
        if "SELECT *" in sparql.upper():
            warnings.append("Consider using explicit variables instead of SELECT *")

        # Check for missing LIMIT on potentially large result sets
        if "LIMIT" not in sparql.upper() and "COUNT" not in sparql.upper():
            warnings.append("Consider adding LIMIT to restrict result size")

        return warnings

    def _extract_where_clause(self, sparql: str) -> str:
        """Extract the WHERE clause from SPARQL."""
        match = re.search(r"WHERE\s*\{(.+?)\}", sparql, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
        return ""
