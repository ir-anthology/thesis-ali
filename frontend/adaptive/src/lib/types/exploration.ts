export type Facet = 'author' | 'venue' | 'year' | 'publication';
export type ResultType = 'facet_table' | 'entity_list' | 'comparison' | 'timeline' | 'summary';
export type SortDirection = 'asc' | 'desc';
export type MessageRole = 'user' | 'assistant';
export type ResponseStatus = 'answerable' | 'unsupported' | 'error';

export interface ConversationTurn {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  loading?: boolean;
  error?: boolean;
}

export interface Filter {
  facet: Facet;
  value: string;
  label: string;
}

export interface SortState {
  field: string;
  direction: SortDirection;
}

export interface ResultColumn {
  key: string;
  label: string;
  type: 'text' | 'number' | 'badge' | 'link';
  sortable?: boolean;
}

export interface ResultRow {
  [key: string]: string | number;
}

export interface ResultState {
  type: ResultType;
  columns: ResultColumn[];
  rows: ResultRow[];
  title?: string;
}

export interface Observation {
  id: string;
  text: string;
  source: 'llm';
}

export interface FollowUpQuestion {
  id: string;
  text: string;
}

export interface Entity {
  id: string;
  name: string;
  type: Facet;
  facets: Record<string, string | number>;
}

export interface ExplorationContext {
  filters: Filter[];
  targetFacet: Facet | null;
  sorting: SortState | null;
  selectedEntities: Entity[];
}

export interface InterpretationState {
  observations: Observation[];
  suggestions: FollowUpQuestion[];
}

export interface ExplorationState {
  conversation: ConversationTurn[];
  context: ExplorationContext;
  result: ResultState | null;
  interpretation: InterpretationState;
  loading: boolean;
  error: string | null;
  activeView: ResultType | null;
}

export interface ExplorationResponse {
  status: ResponseStatus;
  conversation: ConversationTurn[];
  exploration: {
    targetFacet: Facet | null;
    filters: Filter[];
    sort: SortState | null;
  };
  result: ResultState;
  interpretation: InterpretationState;
}
