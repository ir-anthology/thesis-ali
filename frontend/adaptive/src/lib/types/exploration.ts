/**
 * Exploration State Types
 *
 * This module defines the core data types for the IR Anthology Chat application.
 * The types model a conversation-driven exploration of scholarly knowledge graphs,
 * where the UI adapts dynamically based on user queries and interactions.
 *
 * Key Concepts:
 * - Conversation: A series of user/assistant turns that form the exploration context
 * - Result: The structured data returned from the knowledge graph
 * - Observations: LLM-generated insights about the current exploration state
 * - Suggestions: Suggested next questions based on the current context
 */

/** The type of visualization to render for result data */
export type ResultType = 'facet_table';

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

export interface InterpretationState {
  observations: string[];
  suggestions: string[];
}

export interface HistoryTurn {
  role: MessageRole;
  content: string;
  result?: ResultState;
  observations?: string[];
  suggestions?: string[];
  sparql_query?: string;
  status?: ResponseStatus;
}

export interface ExplorationResponse {
  status: ResponseStatus;
  result: ResultState;
  interpretation: InterpretationState;
  sparql_query?: string;
}
