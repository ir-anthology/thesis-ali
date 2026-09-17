import type { ResultColumn, ResultRow } from '$lib/types/exploration';

export const overviewData: { title: string; columns: ResultColumn[]; rows: ResultRow[] } = {
  title: 'Knowledge Graph Overview',
  columns: [
    { key: 'authors', label: 'Authors', type: 'number', sortable: true, visible: true, external_link: false, related_column: null },
    { key: 'venues', label: 'Venues', type: 'number', sortable: true, visible: true, external_link: false, related_column: null },
    { key: 'years', label: 'Years', type: 'number', sortable: true, visible: true, external_link: false, related_column: null },
    { key: 'publications', label: 'Publications', type: 'number', sortable: true, visible: true, external_link: false, related_column: null }
  ],
  rows: [
    {
      authors: { value: 50, question: 'Who are the most prolific authors?' },
      venues: { value: 12, question: 'Which venues do they publish in?' },
      years: { value: 5, question: 'Show me publication trends over time' },
      publications: { value: 42, question: 'Who are the most prolific authors?' }
    }
  ]
};
