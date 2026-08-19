import re


def is_sparql(text: str) -> bool:
    text_upper = text.upper().strip()
    sparql_keywords = ["SELECT", "CONSTRUCT", "ASK", "DESCRIBE", "INSERT", "DELETE"]
    has_keyword = any(text_upper.startswith(kw) for kw in sparql_keywords)
    has_prefix = "PREFIX " in text_upper
    has_where = "WHERE " in text_upper
    return has_keyword or has_prefix or has_where
