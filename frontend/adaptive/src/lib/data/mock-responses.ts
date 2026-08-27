import type { ExplorationResponse } from '$lib/types/exploration';

export const mockResponses: Record<string, ExplorationResponse> = {
  'full-response': {
    intent: 'User is asking for the most prolific authors based on publication count.',
    columns: [
      { key: 'author', label: 'Author', type: 'text', sortable: true },
      { key: 'publications', label: 'Publications', type: 'number', sortable: true },
      { key: 'venues', label: 'Venues', type: 'number', sortable: true },
      { key: 'years', label: 'Years', type: 'text' }
    ],
    rows: [
      { author: 'Marti A. Hearst', publications: 42, venues: 12, years: '1995–2024' },
      { author: 'Ryen W. White', publications: 38, venues: 10, years: '2003–2024' },
      { author: 'Gary Marchionini', publications: 31, venues: 9, years: '1997–2023' },
      { author: 'Daniel M. Russell', publications: 27, venues: 8, years: '2000–2022' },
      { author: 'Andrei Z. Broder', publications: 24, venues: 7, years: '1998–2021' }
    ],
    observations: ['Marti A. Hearst leads with 42 publications spanning nearly three decades, indicating sustained research activity in exploratory search.'],
    suggestions: ['Only consider the last five years', 'Which venues do these authors publish in?', 'Show me how this changed over time'],
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
LIMIT 5`
  },

  'limitation-response': {
    intent: 'User is asking about citation counts for publications.',
    limitation: 'I don\'t have data on citation counts. The knowledge graph only contains information about authors, venues, and publications.',
    suggestions: ['Who are the most prolific authors?', 'Which venues do they publish in?']
  },

  'clarification-response': {
    intent: 'User is asking about something ambiguous.',
    clarification: 'Could you clarify whether you are looking for authors, venues, or publications?',
    suggestions: ['Show me the most prolific authors', 'Show me publication venues']
  }
};
