import type { ExplorationResponse } from "$lib/types/exploration";

export const mockResponses: Record<string, ExplorationResponse> = {
  "full-response": {
    intent:
      "Here is the table that shows the most prolific authors based on publication count.",
    columns: [
      { key: "author", label: "Author", type: "text", sortable: true },
      {
        key: "publications",
        label: "Publications",
        type: "number",
        sortable: true,
      },
      { key: "venues", label: "Venues", type: "number", sortable: true },
      { key: "years", label: "Years", type: "text" },
    ],
    rows: [
      {
        author: {
          value: "Marti A. Hearst",
          question: "Tell me about Marti A. Hearst",
        },
        publications: {
          value: 42,
          question: "How many publications does Marti A. Hearst have?",
        },
        venues: {
          value: 12,
          question: "Which venues does Marti A. Hearst publish in?",
        },
        years: {
          value: "1995–2024",
          question: "What years was Marti A. Hearst active?",
        },
      },
      {
        author: {
          value: "Ryen W. White",
          question: "Tell me about Ryen W. White",
        },
        publications: {
          value: 38,
          question: "How many publications does Ryen W. White have?",
        },
        venues: {
          value: 10,
          question: "Which venues does Ryen W. White publish in?",
        },
        years: {
          value: "2003–2024",
          question: "What years was Ryen W. White active?",
        },
      },
      {
        author: {
          value: "Gary Marchionini",
          question: "Tell me about Gary Marchionini",
        },
        publications: {
          value: 31,
          question: "How many publications does Gary Marchionini have?",
        },
        venues: {
          value: 9,
          question: "Which venues does Gary Marchionini publish in?",
        },
        years: {
          value: "1997–2023",
          question: "What years was Gary Marchionini active?",
        },
      },
      {
        author: {
          value: "Daniel M. Russell",
          question: "Tell me about Daniel M. Russell",
        },
        publications: {
          value: 27,
          question: "How many publications does Daniel M. Russell have?",
        },
        venues: {
          value: 8,
          question: "Which venues does Daniel M. Russell publish in?",
        },
        years: {
          value: "2000–2022",
          question: "What years was Daniel M. Russell active?",
        },
      },
      {
        author: {
          value: "Andrei Z. Broder",
          question: "Tell me about Andrei Z. Broder",
        },
        publications: {
          value: 24,
          question: "How many publications does Andrei Z. Broder have?",
        },
        venues: {
          value: 7,
          question: "Which venues does Andrei Z. Broder publish in?",
        },
        years: {
          value: "1998–2021",
          question: "What years was Andrei Z. Broder active?",
        },
      },
    ],
    observations: [
      "Marti A. Hearst leads with 42 publications spanning nearly three decades, indicating sustained research activity in exploratory search.",
    ],
    suggestions: [
      "Who are the most prolific authors?",
      "What about citation counts?",
      "Tell me about something",
    ],
    sparql_query: `PREFIX schema: <http://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?author
       (COUNT(?pub) AS ?publications)
       (COUNT(DISTINCT ?venue) AS ?venues)
       (CONCAT(MIN(STR(?year)), "\u2013", MAX(STR(?year))) AS ?years)
WHERE {
  ?pub a schema:ScholarlyArticle ;
       dcterms:creator ?author ;
       schema:isPartOf ?venue ;
       dcterms:date ?year .
}
GROUP BY ?author
ORDER BY DESC(?publications)
LIMIT 5`,
  },

  "limitation-response": {
    intent: "User is asking about citation counts for publications.",
    limitation:
      "I don't have data on citation counts. The knowledge graph only contains information about authors, venues, and publications.",
    suggestions: [
      "Who are the most prolific authors?",
      "What about citation counts?",
      "Tell me about something",
    ],
  },

  "clarification-response": {
    intent: "User is asking about something ambiguous.",
    clarification:
      "Could you clarify whether you are looking for authors, venues, or publications?",
    suggestions: [
      "Who are the most prolific authors?",
      "What about citation counts?",
      "Tell me about something",
    ],
  },
};
