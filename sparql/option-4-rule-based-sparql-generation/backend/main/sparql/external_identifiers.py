"""Deterministic augmentation of grouped SPARQL queries.

The LLM generates the query shape, but the external-identifier policy is fixed
by the application.  Keeping this transformation deterministic avoids asking
the LLM to invent or substitute identifiers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class _IdentifierSpec:
    entity_type: str
    property_name: str
    variable_name: str


_SPECS = {
    "author": _IdentifierSpec("author", "orcid", "orcid"),
    "publication": _IdentifierSpec("publication", "doi", "doi"),
    "venue": _IdentifierSpec("venue", "issn", "issn"),
}

_GROUP_BY_RE = re.compile(
    r"\bGROUP\s+BY\b(?P<variables>.*?)(?=\bHAVING\b|\bORDER\s+BY\b|\bLIMIT\b|\bOFFSET\b|$)",
    re.IGNORECASE | re.DOTALL,
)
_VARIABLE_RE = re.compile(r"\?(?P<name>[A-Za-z_][A-Za-z0-9_]*)")
_WHERE_RE = re.compile(r"\bWHERE\s*\{", re.IGNORECASE)


def extend_with_external_identifier(sparql: str) -> str:
    """Add the preferred optional identifier for a supported grouped entity.

    The function is intentionally best-effort.  If the query is not a shape
    produced by the supported generator patterns, it is returned unchanged so
    that this policy stage cannot make an otherwise executable query fail.
    """
    if not sparql or not sparql.strip():
        return sparql

    group_match = _GROUP_BY_RE.search(sparql)
    if group_match is None:
        return sparql

    grouped_variables = [
        match.group("name")
        for match in _VARIABLE_RE.finditer(group_match.group("variables"))
    ]
    if not grouped_variables:
        return sparql

    where_start = _WHERE_RE.search(sparql)
    if where_start is None:
        return sparql
    where = sparql[where_start.end() : group_match.start()]

    candidate = _find_candidate(grouped_variables, where)
    if candidate is None:
        return sparql

    spec, entity_variable = candidate
    identifier_variable = f"?{spec.variable_name}"
    identifier_property = f"dblp:{spec.property_name}"

    select_start = re.search(r"\bSELECT\b", sparql, re.IGNORECASE)
    if select_start is None:
        return sparql
    select_end = where_start.start()
    select_clause = sparql[select_start.end() : select_end]

    result = sparql
    if not re.search(rf"\?{re.escape(spec.variable_name)}\b", select_clause):
        result = (
            result[:select_end]
            + f" {identifier_variable} "
            + result[select_end:]
        )
        group_match = _GROUP_BY_RE.search(result)
        if group_match is None:
            return sparql

    group_variables_text = group_match.group("variables")
    if not re.search(
        rf"\?{re.escape(spec.variable_name)}\b", group_variables_text
    ):
        insert_at = group_match.end("variables")
        while insert_at > group_match.start() and result[insert_at - 1].isspace():
            insert_at -= 1
        result = result[:insert_at] + f" {identifier_variable}" + result[insert_at:]

    if not re.search(
        rf"\b{re.escape(identifier_property)}\b", result, re.IGNORECASE
    ):
        optional = (
            "OPTIONAL { "
            f"{entity_variable} {identifier_property} {identifier_variable} . "
            "}\n"
        )
        where_match = _WHERE_RE.search(result)
        group_match = _GROUP_BY_RE.search(result)
        if where_match is None or group_match is None:
            return sparql
        where_close = _where_close_index(result, where_match)
        if where_close is None:
            return sparql
        result = result[:where_close] + optional + result[where_close:]

    return result


def _find_candidate(
    grouped_variables: list[str], where: str
) -> tuple[_IdentifierSpec, str] | None:
    """Infer the grouped entity and its subject variable from query patterns."""
    for grouped_name in grouped_variables:
        grouped_variable = f"?{grouped_name}"
        lower_name = grouped_name.lower()

        if "year" in lower_name or re.search(
            rf"\?\w+\s+dblp:yearOf(?:Publication|Event)\s+\?{re.escape(grouped_name)}\b",
            where,
            re.IGNORECASE,
        ):
            continue

        direct_type = _type_from_name(lower_name)
        if direct_type is not None:
            entity_variable = _entity_variable_for_group(
                grouped_variable, direct_type, where
            )
            if entity_variable is not None:
                return _SPECS[direct_type], entity_variable

        for entity_type, predicates in (
            ("author", ("primaryCreatorName", "creatorName")),
            ("publication", ("title",)),
            ("venue", ("primaryStreamTitle", "streamTitle")),
        ):
            for predicate in predicates:
                match = re.search(
                    rf"(?P<entity>\?\w+)\s+dblp:{predicate}\s+{re.escape(grouped_variable)}\b",
                    where,
                    re.IGNORECASE,
                )
                if match:
                    return _SPECS[entity_type], match.group("entity")

    return None


def _type_from_name(name: str) -> str | None:
    if any(token in name for token in ("author", "creator")):
        return "author"
    if any(token in name for token in ("venue", "stream", "journal", "conference")):
        return "venue"
    if any(token in name for token in ("publication", "pub", "paper", "article")):
        return "publication"
    return None


def _entity_variable_for_group(
    grouped_variable: str, entity_type: str, where: str
) -> str | None:
    """Return the entity subject associated with a grouped variable."""
    if re.search(rf"\b{re.escape(grouped_variable)}\b", where):
        if _looks_like_entity_variable(grouped_variable, entity_type):
            return grouped_variable

    predicates = {
        "author": ("primaryCreatorName", "creatorName"),
        "publication": ("title",),
        "venue": ("primaryStreamTitle", "streamTitle"),
    }[entity_type]
    for predicate in predicates:
        match = re.search(
            rf"(?P<entity>\?\w+)\s+dblp:{predicate}\s+{re.escape(grouped_variable)}\b",
            where,
            re.IGNORECASE,
        )
        if match:
            return match.group("entity")
    return None


def _looks_like_entity_variable(variable: str, entity_type: str) -> bool:
    name = variable.removeprefix("?").lower()
    if name.endswith(("_name", "name", "_title", "title", "_label", "label")):
        return False
    if entity_type == "author":
        return any(token in name for token in ("author", "creator"))
    if entity_type == "publication":
        return any(token in name for token in ("publication", "pub", "paper", "article"))
    return any(token in name for token in ("venue", "stream", "journal", "conference"))


def _where_close_index(sparql: str, where_match: re.Match[str]) -> int | None:
    """Find the closing brace for the main WHERE group."""
    opening = sparql.find("{", where_match.start(), where_match.end())
    if opening < 0:
        return None

    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(opening, len(sparql)):
        character = sparql[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in ('"', "'"):
            quote = character
        elif character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return index
    return None
