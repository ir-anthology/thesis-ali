SPARQL_QUERY = """\
PREFIX dblp: <https://dblp.org/rdf/schema#>

SELECT
  ?pubTitle
  (COUNT(DISTINCT ?authorName) AS ?Authors)
  (COUNT(DISTINCT ?venue) AS ?Venues)
  (COUNT(DISTINCT ?year) AS ?Years)
WHERE {
  ?pub a dblp:Publication .
  ?pub dblp:title ?pubTitle .

  OPTIONAL {
    ?pub dblp:authoredBy ?author .
    ?author dblp:primaryCreatorName ?authorName .
  }

  OPTIONAL {
    ?pub dblp:publishedIn ?venue .
  }

  OPTIONAL {
    ?pub dblp:yearOfPublication ?year .
  }
}
GROUP BY ?pubTitle
ORDER BY ASC(?pubTitle) 
LIMIT 10\
"""


def execute(request: str) -> str:
    return SPARQL_QUERY
