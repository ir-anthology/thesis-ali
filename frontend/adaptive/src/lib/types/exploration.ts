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
 */

/** The role of a message in the conversation */
export type MessageRole = 'user' | 'assistant';

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

export interface HistoryTurn {
  role: MessageRole;
  content: string;
  response_text?: string;
  columns?: ResultColumn[];
  rows?: ResultRow[];
  observations?: string[];
  suggestions?: string[];
  sparql_query?: string;
}

export interface ExplorationResponse {
  response_text: string;
  columns?: ResultColumn[];
  rows?: ResultRow[];
  observations?: string[];
  suggestions?: string[];
  sparql_query?: string;
}
