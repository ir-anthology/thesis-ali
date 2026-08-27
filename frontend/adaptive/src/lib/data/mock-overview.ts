import type { ResultState } from '$lib/types/exploration';

export const overviewData: ResultState & { title: string } = {
  type: 'facet_table',
  title: 'Knowledge Graph Overview',
  columns: [
    { key: 'authors', label: 'Authors', type: 'number' },
    { key: 'venues', label: 'Venues', type: 'number' },
    { key: 'years', label: 'Years', type: 'number' },
    { key: 'publications', label: 'Publications', type: 'number' }
  ],
  rows: [
    { authors: 50, venues: 12, years: 5, publications: 42 }
  ]
};

export const overviewQueryMap: Record<string, string> = {
  authors: 'Who are the most prolific authors?',
  venues: 'Which venues do they publish in?',
  years: 'Show me publication trends over time',
  publications: 'Who are the most prolific authors?'
};
