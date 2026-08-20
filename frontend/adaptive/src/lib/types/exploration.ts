/**
 * Exploration State Types
 *
 * This module defines the core data types for the Scholarly Explorer application.
 * The types model a conversation-driven exploration of scholarly knowledge graphs,
 * where the UI adapts dynamically based on user queries and interactions.
 *
 * Key Concepts:
 * - Conversation: A series of user/assistant turns that form the exploration context
 * - Facet: The primary dimension of exploration (author, venue, year, publication)
 * - Result: The structured data returned from the knowledge graph
 * - Observation: LLM-generated insights about the current exploration state
 * - Follow-up: Suggested next questions based on the current context
 */

/** The primary dimensions for exploring scholarly data */
export type Facet = 'author' | 'venue' | 'year' | 'publication';

/** The type of visualization to render for result data */
export type ResultType = 'facet_table' | 'entity_list' | 'comparison' | 'timeline' | 'summary';

/** Sort direction for table columns */
export type SortDirection = 'asc' | 'desc';

/** The role of a message in the conversation */
export type MessageRole = 'user' | 'assistant';

/** The status of an exploration response from the backend */
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
  sparql_query?: string;
}
