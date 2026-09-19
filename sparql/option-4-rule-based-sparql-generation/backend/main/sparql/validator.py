"""SPARQL query validation — rule-based checks before execution."""

from __future__ import annotations

import re
import logging

from pydantic import BaseModel, Field

from backend.main.schema.provider import DBLPSchemaProvider

logger = logging.getLogger(__name__)

_schema = DBLPSchemaProvider()

_CLASS_REFERENCE_RE = re.compile(
    r"(?P<type>\ba\b|rdf:type)\s+dblp:(?P<class>\w+)",
    re.IGNORECASE,
)


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
        structure_errors, structure_warnings = self._validate_structure(sparql)
        errors.extend(structure_errors)
        warnings.extend(structure_warnings)

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

        # Classes are objects of `a`/`rdf:type`, not predicates. Mask only
        # those occurrences so the same name is still rejected if it appears
        # in predicate position.
        where_without_class_references = _CLASS_REFERENCE_RE.sub(
            lambda match: f"{match.group('type')} __DBLP_CLASS__",
            where,
        )
        for pred in re.findall(r"dblp:(\w+)", where_without_class_references):
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
        for match in _CLASS_REFERENCE_RE.finditer(where):
            cls = match.group("class")
            if cls not in known:
                errors.append(f"Unknown class: dblp:{cls}")
        return errors

    @staticmethod
    def _validate_structure(sparql: str) -> tuple[list[str], list[str]]:
        warnings: list[str] = []
        if "SELECT *" in sparql.upper():
            warnings.append("Consider using explicit variables instead of SELECT *")
        return [], warnings


def _extract_where_clause(sparql: str) -> str:
    match = re.search(r"WHERE\s*\{(.+?)\}", sparql, re.IGNORECASE | re.DOTALL)
    return match.group(1) if match else ""
