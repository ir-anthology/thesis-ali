export type Facet = 'author' | 'venue' | 'year' | 'publication';

export const ALL_FACETS: Facet[] = ['author', 'venue', 'year', 'publication'];

export const FACET_LABELS: Record<Facet, string> = {
  author: 'Author',
  venue: 'Venue',
  year: 'Year',
  publication: 'Publication'
};

export interface Filter {
  field: Facet;
  operator: '=' | '>=' | '<=';
  value: string | number;
}

export interface FacetRow {
  targetValue: string | number;
  connections: Record<Facet, number | string>;
}

export interface SortState {
  facet: Facet;
  direction: 'asc' | 'desc';
}

export interface Observation {
  id: string;
  text: string;
}

export interface FollowUpQuestion {
  id: string;
  text: string;
}

export type LoadingStage =
  | 'interpreting'
  | 'preparing'
  | 'querying'
  | 'analyzing'
  | null;

export type ErrorType = 'generic' | 'unavailable' | 'unsupported';

export interface ErrorState {
  type: ErrorType;
  message: string;
  suggestions?: string[];
}

export interface GeneratedPrompt {
  text: string;
  targetCell?: { rowIndex: number; facet: Facet };
}

export interface ExplorationState {
  input: string;
  targetFacet: Facet | null;
  filters: Filter[];
  sorting: SortState | null;
  rows: FacetRow[];
  observations: Observation[];
  followUpQuestions: FollowUpQuestion[];
  loadingStage: LoadingStage;
  error: ErrorState | null;
  promptOutputMode: 'input' | 'tooltip';
  generatedPrompt: GeneratedPrompt | null;
  hasSubmitted: boolean;
}
