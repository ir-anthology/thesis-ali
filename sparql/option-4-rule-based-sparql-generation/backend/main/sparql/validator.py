"""SPARQL query validation — rule-based checks before execution."""

from __future__ import annotations

import re
import logging

from pydantic import BaseModel, Field

from backend.main.schema.provider import DBLPSchemaProvider

logger = logging.getLogger(__name__)

_schema = DBLPSchemaProvider()


class ValidationResult(BaseModel):
    """Result of validating a SPARQL query."""

    valid: bool = Field(default=False)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class SPARQLValidator:
    """Validates SPARQL queries before execution."""

    def validate(self, sparql: str) -> ValidationResult:
        if not sparql or not sparql.strip():
            return ValidationResult(valid=False, errors=["Empty SPARQL query"])

        errors: list[str] = []
        warnings: list[str] = []

        errors.extend(self._validate_syntax(sparql))
        errors.extend(self._validate_prefixes(sparql))
        errors.extend(self._validate_predicates(sparql))
        errors.extend(self._validate_classes(sparql))
        warnings.extend(self._validate_structure(sparql))

        valid = len(errors) == 0
        if valid:
            logger.info("SPARQL validation passed (%d warnings)", len(warnings))
        else:
            logger.warning("SPARQL validation failed: %s", errors)

        return ValidationResult(valid=valid, errors=errors, warnings=warnings)

    # ------------------------------------------------------------------

    @staticmethod
    def _validate_syntax(sparql: str) -> list[str]:
        errors: list[str] = []
        upper = sparql.strip().upper()
        non_prefix = [
            l for l in upper.split("\n") if not l.strip().startswith("PREFIX")
        ]
        body = "\n".join(non_prefix).strip()

        if not body.startswith("SELECT"):
            errors.append("Query must start with SELECT")

        if "{" not in sparql or "}" not in sparql:
            errors.append("Missing WHERE clause braces")

        if sparql.count("{") != sparql.count("}"):
            errors.append("Unbalanced braces in query")

        return errors

    @staticmethod
    def _validate_prefixes(sparql: str) -> list[str]:
        errors: list[str] = []
        if "dblp:" in sparql and "PREFIX dblp:" not in sparql:
            errors.append("Missing PREFIX declaration for dblp:")
        if "rdf:" in sparql and "PREFIX rdf:" not in sparql:
            errors.append("Missing PREFIX declaration for rdf:")
        if "xsd:" in sparql and "PREFIX xsd:" not in sparql:
            errors.append("Missing PREFIX declaration for xsd:")
        return errors

    @staticmethod
    def _validate_predicates(sparql: str) -> list[str]:
        errors: list[str] = []
        known = set(_schema.get_predicates())
        where = _extract_where_clause(sparql)
        if not where:
            return errors
        for pred in re.findall(r"dblp:(\w+)", where):
            if pred not in known:
                errors.append(f"Unknown predicate: dblp:{pred}")
        return errors

    @staticmethod
    def _validate_classes(sparql: str) -> list[str]:
        errors: list[str] = []
        known = set(_schema.get_classes())
        where = _extract_where_clause(sparql)
        if not where:
            return errors
        for cls in re.findall(r"\ba\s+dblp:(\w+)", where):
            if cls not in known:
                errors.append(f"Unknown class: dblp:{cls}")
        return errors

    @staticmethod
    def _validate_structure(sparql: str) -> list[str]:
        warnings: list[str] = []
        if "SELECT *" in sparql.upper():
            warnings.append("Consider using explicit variables instead of SELECT *")
        if "LIMIT" not in sparql.upper() and "COUNT" not in sparql.upper():
            warnings.append("Consider adding LIMIT to restrict result size")
        return warnings


def _extract_where_clause(sparql: str) -> str:
    match = re.search(r"WHERE\s*\{(.+?)\}", sparql, re.IGNORECASE | re.DOTALL)
    return match.group(1) if match else ""
