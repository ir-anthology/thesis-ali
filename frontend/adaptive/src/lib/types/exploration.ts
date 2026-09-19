/**
 * Exploration State Types
 *
 * This module defines the core data types for the IR Anthology Chat application.
 * The types model a conversation-driven exploration of scholarly knowledge graphs,
 * where the UI adapts dynamically based on user queries and interactions.
 *
 * Key Concepts:
 * - Conversation: A series of user/assistant turns that form the exploration context
 * - Response: A flat structure with optional fields for table data, observations, and suggestions
 * - The UI renders only what's present (columns/rows for tables, observations, suggestions)
 * - interpretation is rendered if present
 */

/** The role of a message in the conversation */
export type MessageRole = 'user' | 'assistant';

export type StreamStage =
  | 'interpreting'
  | 'generating_sparql'
  | 'obtaining_results'
  | 'generating_observations'
  | 'creating_suggestions';

export interface ConversationTurn {
  id: string;
  parentId: string | null;
  role: MessageRole;
  content: string;
  timestamp: Date;
  loading?: boolean;
  streaming?: boolean;
  streamingStage?: StreamStage;
  streamingMessage?: string;
  pending?: boolean;
  pendingMessage?: string;
  error?: boolean;
  branchCount?: number;
}

export interface ResultColumn {
  key: string;
  label: string;
  type: 'text' | 'number' | 'badge' | 'link';
  sortable: boolean;
  visible: boolean;
  external_link: boolean;
  related_column: string | null;
}

export type EntityType = 'author' | 'venue' | 'publication' | 'entity';

export interface CellMetadata {
  entity_id?: string;
  entity_type?: EntityType;
  [key: string]: string | number | boolean | undefined;
}

export interface CellQuestionContext {
  column: string;
  value: string | number;
  row: Record<string, string | number>;
  metadata?: Record<string, CellMetadata>;
  interpretation?: string;
}

export interface CellValue {
  value: string | number;
  question: string;
  metadata?: CellMetadata;
}

export interface ResultRow {
  [key: string]: CellValue;
}

export interface HistoryTurn {
  role: MessageRole;
  content: string;
  interpretation?: string | null;
  columns?: ResultColumn[];
  rows?: ResultRow[];
  observations?: string[];
  suggestions?: string[];
  sparql_query?: string;
}

export interface ExplorationResponse {
  interpretation?: string | null;
  columns?: ResultColumn[];
  rows?: ResultRow[];
  observations?: string[];
  suggestions?: string[];
  sparql_query?: string;
}

export interface EntityInteraction {
  entity_id: string;
  entity_type?: EntityType;
}

export interface StatisticsResponse {
  columns: ResultColumn[];
  rows: ResultRow[];
}
