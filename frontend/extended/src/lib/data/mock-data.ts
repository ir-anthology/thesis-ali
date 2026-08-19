import type { Facet, Filter, FacetRow, Observation, FollowUpQuestion } from '$lib/types/exploration';

export const initialSummary = {
  authors: 1245,
  venues: 320,
  years: 35,
  publications: 250000
};

const authorRows: FacetRow[] = [
  { targetValue: 'Author A', connections: { author: 'Author A', venue: 12, year: 5, publication: 42 } },
  { targetValue: 'Author B', connections: { author: 'Author B', venue: 8, year: 4, publication: 31 } },
  { targetValue: 'Author C', connections: { author: 'Author C', venue: 6, year: 3, publication: 25 } },
  { targetValue: 'Author D', connections: { author: 'Author D', venue: 15, year: 7, publication: 58 } },
  { targetValue: 'Author E', connections: { author: 'Author E', venue: 4, year: 2, publication: 12 } },
  { targetValue: 'Author F', connections: { author: 'Author F', venue: 9, year: 6, publication: 37 } },
  { targetValue: 'Author G', connections: { author: 'Author G', venue: 3, year: 2, publication: 8 } },
  { targetValue: 'Author H', connections: { author: 'Author H', venue: 11, year: 5, publication: 44 } },
  { targetValue: 'Author I', connections: { author: 'Author I', venue: 7, year: 4, publication: 29 } },
  { targetValue: 'Author J', connections: { author: 'Author J', venue: 5, year: 3, publication: 18 } }
];

const venueRows: FacetRow[] = [
  { targetValue: 'Venue Alpha', connections: { author: 240, venue: 'Venue Alpha', year: 15, publication: 1200 } },
  { targetValue: 'Venue Beta', connections: { author: 180, venue: 'Venue Beta', year: 12, publication: 890 } },
  { targetValue: 'Venue Gamma', connections: { author: 95, venue: 'Venue Gamma', year: 8, publication: 420 } },
  { targetValue: 'Venue Delta', connections: { author: 60, venue: 'Venue Delta', year: 6, publication: 280 } },
  { targetValue: 'Venue Epsilon', connections: { author: 45, venue: 'Venue Epsilon', year: 4, publication: 150 } }
];

const yearRows: FacetRow[] = [
  { targetValue: 2025, connections: { author: 320, venue: 45, year: 2025, publication: 2800 } },
  { targetValue: 2024, connections: { author: 580, venue: 120, year: 2024, publication: 8500 } },
  { targetValue: 2023, connections: { author: 520, venue: 110, year: 2023, publication: 7800 } },
  { targetValue: 2022, connections: { author: 480, venue: 100, year: 2022, publication: 7200 } },
  { targetValue: 2021, connections: { author: 430, venue: 90, year: 2021, publication: 6500 } },
  { targetValue: 2020, connections: { author: 390, venue: 85, year: 2020, publication: 5800 } }
];

const authorAVenueRows: FacetRow[] = [
  { targetValue: 'Venue Alpha', connections: { author: 'Author A', venue: 'Venue Alpha', year: 3, publication: 15 } },
  { targetValue: 'Venue Beta', connections: { author: 'Author A', venue: 'Venue Beta', year: 2, publication: 12 } },
  { targetValue: 'Venue Gamma', connections: { author: 'Author A', venue: 'Venue Gamma', year: 2, publication: 8 } },
  { targetValue: 'Venue Delta', connections: { author: 'Author A', venue: 'Venue Delta', year: 1, publication: 4 } },
  { targetValue: 'Venue Epsilon', connections: { author: 'Author A', venue: 'Venue Epsilon', year: 1, publication: 3 } }
];

const authorAYearRows: FacetRow[] = [
  { targetValue: 2025, connections: { author: 'Author A', venue: 3, year: 2025, publication: 12 } },
  { targetValue: 2024, connections: { author: 'Author A', venue: 5, year: 2024, publication: 15 } },
  { targetValue: 2023, connections: { author: 'Author A', venue: 4, year: 2023, publication: 10 } },
  { targetValue: 2022, connections: { author: 'Author A', venue: 2, year: 2022, publication: 5 } }
];

const venueAlphaAuthorRows: FacetRow[] = [
  { targetValue: 'Author A', connections: { author: 'Author A', venue: 'Venue Alpha', year: 3, publication: 15 } },
  { targetValue: 'Author D', connections: { author: 'Author D', venue: 'Venue Alpha', year: 5, publication: 22 } },
  { targetValue: 'Author H', connections: { author: 'Author H', venue: 'Venue Alpha', year: 4, publication: 18 } },
  { targetValue: 'Author B', connections: { author: 'Author B', venue: 'Venue Alpha', year: 2, publication: 8 } },
  { targetValue: 'Author F', connections: { author: 'Author F', venue: 'Venue Alpha', year: 3, publication: 11 } }
];

const authorDRows: FacetRow[] = [
  { targetValue: 'Venue Alpha', connections: { author: 'Author D', venue: 'Venue Alpha', year: 5, publication: 22 } },
  { targetValue: 'Venue Beta', connections: { author: 'Author D', venue: 'Venue Beta', year: 4, publication: 18 } },
  { targetValue: 'Venue Gamma', connections: { author: 'Author D', venue: 'Venue Gamma', year: 3, publication: 12 } },
  { targetValue: 'Venue Epsilon', connections: { author: 'Author D', venue: 'Venue Epsilon', year: 2, publication: 6 } }
];

const filteredDataMap: Record<string, FacetRow[]> = {
  'author|Author A|venue': authorAVenueRows,
  'author|Author A|year': authorAYearRows,
  'venue|Venue Alpha|author': venueAlphaAuthorRows,
  'author|Author D|venue': authorDRows
};

function getFilteredRows(filters: Filter[], targetFacet: Facet): FacetRow[] {
  if (filters.length === 0) return [];
  const filter = filters[0];
  const key = `${filter.field}|${filter.value}|${targetFacet}`;
  return filteredDataMap[key] ?? [];
}

export const defaultObservations: Observation[] = [
  { id: '1', text: 'Author A and Author D are the most active contributors, with 42 and 58 publications respectively.' },
  { id: '2', text: 'Publication activity spans multiple venues, with Venue Alpha being the most frequent.' },
  { id: '3', text: 'There is a clear increasing trend in publications over recent years, peaking in 2024.' },
  { id: '4', text: 'Most authors publish across 3-6 distinct venues, suggesting interdisciplinary work.' }
];

export const defaultFollowUps: FollowUpQuestion[] = [
  { id: '1', text: 'How has publication output changed over time?' },
  { id: '2', text: 'Which venues have the most publications?' },
  { id: '3', text: 'Who are the most prolific authors?' },
  { id: '4', text: 'What are the recent trends in this area?' }
];

export const unsupportedResponse = {
  message: 'This question cannot currently be answered using the available scholarly data.',
  suggestions: [
    'Which authors published in Venue Alpha?',
    'Which venues are associated with Author D?',
    'How many publications were there in 2024?',
    'Who are the most prolific authors?'
  ]
};

export function getMockData(
  targetFacet: Facet,
  filters: Filter[]
): { rows: FacetRow[]; observations: Observation[]; followUps: FollowUpQuestion[] } {
  const rows = filters.length > 0
    ? getFilteredRows(filters, targetFacet)
    : getRowsForFacet(targetFacet);

  return {
    rows,
    observations: defaultObservations,
    followUps: defaultFollowUps
  };
}

function getRowsForFacet(facet: Facet): FacetRow[] {
  switch (facet) {
    case 'author': return authorRows;
    case 'venue': return venueRows;
    case 'year': return yearRows;
    case 'publication': return [];
    default: return [];
  }
}
