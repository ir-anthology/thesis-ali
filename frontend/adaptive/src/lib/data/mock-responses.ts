import type { ExplorationResponse } from '$lib/types/exploration';

export const mockResponses: Record<string, ExplorationResponse> = {
  'prolific-authors': {
    status: 'answerable',
    conversation: [],
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
    exploration: {
      targetFacet: 'author',
      filters: [],
      sort: { field: 'publications', direction: 'desc' }
    },
    result: {
      type: 'facet_table',
      title: 'Most Prolific Authors in Exploratory Search',
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
      ]
    },
    interpretation: {
      observations: [
        {
          id: 'obs-1',
          text: 'Marti A. Hearst leads with 42 publications spanning nearly three decades, indicating sustained research activity in exploratory search.',
          source: 'llm'
        }
      ],
      suggestions: [
        { id: 'sug-1', text: 'Only consider the last five years' },
        { id: 'sug-2', text: 'Which venues do these authors publish in?' },
        { id: 'sug-3', text: 'Show me how this changed over time' }
      ]
    }
  },

  'filtered-years': {
    status: 'answerable',
    conversation: [],
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
  FILTER(?year >= 2020 && ?year <= 2025)
}
GROUP BY ?author
ORDER BY DESC(?publications)
LIMIT 5`,
    exploration: {
      targetFacet: 'author',
      filters: [{ facet: 'year', value: '2020-2025', label: '2020–2025' }],
      sort: { field: 'publications', direction: 'desc' }
    },
    result: {
      type: 'facet_table',
      title: 'Most Prolific Authors (2020–2025)',
      columns: [
        { key: 'author', label: 'Author', type: 'text', sortable: true },
        { key: 'publications', label: 'Publications', type: 'number', sortable: true },
        { key: 'venues', label: 'Venues', type: 'number', sortable: true },
        { key: 'years', label: 'Years', type: 'text' }
      ],
      rows: [
        { author: 'Marti A. Hearst', publications: 18, venues: 6, years: '2020–2024' },
        { author: 'Ryen W. White', publications: 16, venues: 5, years: '2020–2024' },
        { author: 'Gary Marchionini', publications: 12, venues: 4, years: '2020–2023' },
        { author: 'Daniel M. Russell', publications: 9, venues: 3, years: '2020–2022' },
        { author: 'Andrei Z. Broder', publications: 7, venues: 3, years: '2020–2021' }
      ]
    },
    interpretation: {
      observations: [
        {
          id: 'obs-2',
          text: 'Filtering to the last five years reduces the result set. Marti A. Hearst still leads with 18 publications.',
          source: 'llm'
        }
      ],
      suggestions: [
        { id: 'sug-4', text: 'Which venues do these authors publish in?' },
        { id: 'sug-5', text: 'Show me how this changed over time' },
        { id: 'sug-6', text: 'Compare the top two authors' }
      ]
    }
  },

  venues: {
    status: 'answerable',
    conversation: [],
    sparql_query: `PREFIX schema: <http://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?venue
       (COUNT(?pub) AS ?publications)
       (COUNT(DISTINCT ?author) AS ?authors)
       (CONCAT(MIN(STR(?year)), "\u2013", MAX(STR(?year))) AS ?years)
WHERE {
  ?pub a schema:ScholarlyArticle ;
       dcterms:creator ?author ;
       schema:isPartOf ?venue ;
       dcterms:date ?year .
  FILTER(?year >= 2020 && ?year <= 2025)
}
GROUP BY ?venue
ORDER BY DESC(?publications)
LIMIT 5`,
    exploration: {
      targetFacet: 'venue',
      filters: [],
      sort: { field: 'publications', direction: 'desc' }
    },
    result: {
      type: 'facet_table',
      title: 'Venues for Top Authors in Exploratory Search',
      columns: [
        { key: 'venue', label: 'Venue', type: 'text', sortable: true },
        { key: 'publications', label: 'Publications', type: 'number', sortable: true },
        { key: 'authors', label: 'Authors', type: 'number', sortable: true },
        { key: 'years', label: 'Years', type: 'text' }
      ],
      rows: [
        { venue: 'SIGIR', publications: 18, authors: 5, years: '2020–2025' },
        { venue: 'CHIIR', publications: 9, authors: 4, years: '2021–2025' },
        { venue: 'CHI', publications: 7, authors: 3, years: '2020–2024' },
        { venue: 'UIST', publications: 5, authors: 2, years: '2020–2023' },
        { venue: 'JASIST', publications: 4, authors: 3, years: '2020–2024' }
      ]
    },
    interpretation: {
      observations: [
        {
          id: 'obs-3',
          text: 'SIGIR dominates as the primary venue, accounting for 18 publications across all five authors.',
          source: 'llm'
        }
      ],
      suggestions: [
        { id: 'sug-7', text: 'Show me how this changed over time' },
        { id: 'sug-8', text: 'Compare SIGIR and CHIIR' },
        { id: 'sug-9', text: 'Why is SIGIR prominent?' }
      ]
    }
  },

  timeline: {
    status: 'answerable',
    conversation: [],
    sparql_query: `PREFIX schema: <http://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?year
       (COUNT(IF(?venueName = "SIGIR", ?pub, NULL)) AS ?SIGIR)
       (COUNT(IF(?venueName = "CHIIR", ?pub, NULL)) AS ?CHIIR)
       (COUNT(IF(?venueName = "CHI", ?pub, NULL)) AS ?CHI)
WHERE {
  ?pub a schema:ScholarlyArticle ;
       schema:isPartOf ?venue ;
       dcterms:date ?year .
  ?venue schema:name ?venueName .
  FILTER(?year >= 2020 && ?year <= 2025)
  FILTER(?venueName IN ("SIGIR", "CHIIR", "CHI"))
}
GROUP BY ?year
ORDER BY ?year`,
    exploration: {
      targetFacet: 'year',
      filters: [],
      sort: { field: 'year', direction: 'asc' }
    },
    result: {
      type: 'timeline',
      title: 'Publication Activity Over Time',
      columns: [
        { key: 'year', label: 'Year', type: 'text' },
        { key: 'SIGIR', label: 'SIGIR', type: 'number' },
        { key: 'CHIIR', label: 'CHIIR', type: 'number' },
        { key: 'CHI', label: 'CHI', type: 'number' }
      ],
      rows: [
        { year: '2020', SIGIR: 12, CHIIR: 3, CHI: 2 },
        { year: '2021', SIGIR: 14, CHIIR: 4, CHI: 2 },
        { year: '2022', SIGIR: 15, CHIIR: 5, CHI: 1 },
        { year: '2023', SIGIR: 16, CHIIR: 6, CHI: 3 },
        { year: '2024', SIGIR: 18, CHIIR: 7, CHI: 2 },
        { year: '2025', SIGIR: 19, CHIIR: 8, CHI: 2 }
      ]
    },
    interpretation: {
      observations: [
        {
          id: 'obs-4',
          text: 'Publication activity at SIGIR shows a steady upward trend, growing from 12 to 19 publications over the period. CHIIR also shows consistent growth.',
          source: 'llm'
        }
      ],
      suggestions: [
        { id: 'sug-10', text: 'Compare SIGIR and CHIIR' },
        { id: 'sug-11', text: 'Which authors contributed most to this growth?' },
        { id: 'sug-12', text: 'Go back to all authors' }
      ]
    }
  },

  comparison: {
    status: 'answerable',
    conversation: [],
    sparql_query: `PREFIX schema: <http://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?venueName
       (COUNT(?pub) AS ?publications)
       (COUNT(DISTINCT ?author) AS ?authors)
       (CONCAT(MIN(STR(?year)), "\u2013", MAX(STR(?year))) AS ?years)
WHERE {
  ?pub a schema:ScholarlyArticle ;
       dcterms:creator ?author ;
       schema:isPartOf ?venue ;
       dcterms:date ?year .
  ?venue schema:name ?venueName .
  FILTER(?venueName IN ("SIGIR", "CHIIR"))
  FILTER(?year >= 2020 && ?year <= 2025)
}
GROUP BY ?venueName`,
    exploration: {
      targetFacet: 'venue',
      filters: [],
      sort: null
    },
    result: {
      type: 'comparison',
      title: 'SIGIR vs CHIIR',
      columns: [
        { key: 'metric', label: 'Metric', type: 'text' },
        { key: 'SIGIR', label: 'SIGIR', type: 'text' },
        { key: 'CHIIR', label: 'CHIIR', type: 'text' }
      ],
      rows: [
        { metric: 'Total Publications', SIGIR: '18', CHIIR: '9' },
        { metric: 'Authors', SIGIR: '5', CHIIR: '4' },
        { metric: 'Years Active', SIGIR: '2020–2025', CHIIR: '2021–2025' },
        { metric: 'Avg Publications/Year', SIGIR: '3.0', CHIIR: '1.8' },
        { metric: 'Growth Trend', SIGIR: 'Increasing', CHIIR: 'Stable' }
      ]
    },
    interpretation: {
      observations: [
        {
          id: 'obs-5',
          text: 'SIGIR has twice the publication volume of CHIIR and shows stronger growth. However, CHIIR has been steadily gaining relevance since its inception.',
          source: 'llm'
        }
      ],
      suggestions: [
        { id: 'sug-13', text: 'Why is SIGIR prominent?' },
        { id: 'sug-14', text: 'Which authors publish in both venues?' },
        { id: 'sug-15', text: 'Show publication trends for all venues' }
      ]
    }
  },

  'why-sigir': {
    status: 'answerable',
    conversation: [],
    sparql_query: `PREFIX schema: <http://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?venueName
       (COUNT(?pub) AS ?publications)
       (COUNT(DISTINCT ?author) AS ?authors)
       (CONCAT(MIN(STR(?year)), "\u2013", MAX(STR(?year))) AS ?years)
WHERE {
  ?pub a schema:ScholarlyArticle ;
       dcterms:creator ?author ;
       schema:isPartOf ?venue ;
       dcterms:date ?year .
  ?venue schema:name ?venueName .
  FILTER(?venueName = "SIGIR")
  FILTER(?year >= 2020 && ?year <= 2025)
}
GROUP BY ?venueName`,
    exploration: {
      targetFacet: 'venue',
      filters: [],
      sort: null
    },
    result: {
      type: 'summary',
      title: 'Why SIGIR Is Prominent',
      columns: [],
      rows: []
    },
    interpretation: {
      observations: [
        {
          id: 'obs-6a',
          text: 'SIGIR (ACM Special Interest Group on Information Retrieval) is the premier venue for information retrieval research. It accounts for the highest publication count in the current result set.',
          source: 'llm'
        },
        {
          id: 'obs-6b',
          text: 'The venue has been active since the 1970s and consistently attracts top researchers in search, retrieval, and exploratory search specifically.',
          source: 'llm'
        },
        {
          id: 'obs-6c',
          text: 'In the current filtered context (top authors, last 5 years), SIGIR represents 38% of all publications.',
          source: 'llm'
        }
      ],
      suggestions: [
        { id: 'sug-16', text: 'Compare SIGIR and CHIIR' },
        { id: 'sug-17', text: 'Which authors publish most at SIGIR?' },
        { id: 'sug-18', text: 'Show all venues' }
      ]
    }
  },

  unsupported: {
    status: 'unsupported',
    conversation: [],
    exploration: {
      targetFacet: null,
      filters: [],
      sort: null
    },
    result: {
      type: 'summary',
      title: 'Unsupported Query',
      columns: [],
      rows: []
    },
    interpretation: {
      observations: [
        {
          id: 'obs-7',
          text: 'I cannot answer that question using the current scholarly data and query capabilities. However, I can help you explore:',
          source: 'llm'
        }
      ],
      suggestions: [
        { id: 'sug-19', text: 'Which authors published in this venue?' },
        { id: 'sug-20', text: 'How did publication activity change over time?' },
        { id: 'sug-21', text: 'Show me the most cited papers' }
      ]
    }
  }
};
