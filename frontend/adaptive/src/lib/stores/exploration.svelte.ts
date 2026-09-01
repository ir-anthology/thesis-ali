/**
 * Exploration Store
 *
 * This module manages the entire exploration state using Svelte 5 runes.
 * It provides a reactive store that handles:
 * - Conversation history (user and assistant turns)
 * - Per-turn response data (columns, rows, observations, suggestions)
 * - Per-turn intent, clarification, limitation
 *
 * The store communicates with the backend API at http://localhost:8000.
 */

import type {
  ConversationTurn,
  ResultColumn,
  ResultRow,
  ExplorationResponse,
  HistoryTurn
} from '$lib/types/exploration';

const API_BASE = 'http://localhost:8000';

function createExplorationStore() {
  let conversation = $state<ConversationTurn[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);

  let intentByTurn = $state<Map<string, string>>(new Map());
  let clarificationByTurn = $state<Map<string, string>>(new Map());
  let limitationByTurn = $state<Map<string, string>>(new Map());
  let columnsByTurn = $state<Map<string, ResultColumn[]>>(new Map());
  let rowsByTurn = $state<Map<string, ResultRow[]>>(new Map());
  let observationsByTurn = $state<Map<string, string[]>>(new Map());
  let suggestionsByTurn = $state<Map<string, string[]>>(new Map());
  let sparqlByTurn = $state<Map<string, string>>(new Map());

  function generateId(): string {
    return crypto.randomUUID();
  }

  function buildHistory(): HistoryTurn[] {
    return conversation.filter(turn => !turn.loading).map((turn) => {
      if (turn.role === 'user') {
        return { role: 'user', content: turn.content };
      }
      return {
        role: 'assistant',
        content: turn.content,
        intent: intentByTurn.get(turn.id),
        clarification: clarificationByTurn.get(turn.id),
        limitation: limitationByTurn.get(turn.id),
        columns: columnsByTurn.get(turn.id),
        rows: rowsByTurn.get(turn.id),
        observations: observationsByTurn.get(turn.id),
        suggestions: suggestionsByTurn.get(turn.id),
        sparql_query: sparqlByTurn.get(turn.id)
      };
    });
  }

  async function sendMessage(content: string): Promise<void> {
    if (!content.trim() || loading) return;

    const userTurn: ConversationTurn = {
      id: generateId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    };
    conversation = [...conversation, userTurn];

    const assistantTurn: ConversationTurn = {
      id: generateId(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      loading: true
    };
    conversation = [...conversation, assistantTurn];
    loading = true;
    error = null;

    const history = buildHistory();

    try {
      const res = await fetch(`${API_BASE}/api/exploration`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content, history })
      });

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }

      const response: ExplorationResponse = await res.json();

      const displayText = response.clarification || response.limitation || response.intent || '';

      conversation = conversation.map((t) =>
        t.id === assistantTurn.id
          ? { ...t, content: displayText, loading: false }
          : t
      );

      if (response.intent) {
        intentByTurn = new Map(intentByTurn).set(assistantTurn.id, response.intent);
      }
      if (response.clarification) {
        clarificationByTurn = new Map(clarificationByTurn).set(assistantTurn.id, response.clarification);
      }
      if (response.limitation) {
        limitationByTurn = new Map(limitationByTurn).set(assistantTurn.id, response.limitation);
      }
      if (response.columns) {
        columnsByTurn = new Map(columnsByTurn).set(assistantTurn.id, response.columns);
      }
      if (response.rows) {
        rowsByTurn = new Map(rowsByTurn).set(assistantTurn.id, response.rows);
      }
      if (response.observations) {
        observationsByTurn = new Map(observationsByTurn).set(assistantTurn.id, response.observations);
      }
      if (response.suggestions) {
        suggestionsByTurn = new Map(suggestionsByTurn).set(assistantTurn.id, response.suggestions);
      }
      if (response.sparql_query) {
        sparqlByTurn = new Map(sparqlByTurn).set(assistantTurn.id, response.sparql_query);
      }
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Unknown error';
      conversation = conversation.map((t) =>
        t.id === assistantTurn.id
          ? {
              ...t,
              content: `Failed to get response: ${message}`,
              loading: false,
              error: true
            }
          : t
      );
      error = message;
    }

    loading = false;
  }

  function selectSuggestion(suggestion: string): void {
    sendMessage(suggestion);
  }

  function retry(): void {
    const lastUserTurn = [...conversation].reverse().find((t) => t.role === 'user');
    if (lastUserTurn) {
      conversation = conversation.filter((t) => !t.loading && !(t.role === 'assistant' && t.error));
      sendMessage(lastUserTurn.content);
    }
  }

  function clearExploration(): void {
    conversation = [];
    loading = false;
    error = null;
    intentByTurn = new Map();
    clarificationByTurn = new Map();
    limitationByTurn = new Map();
    columnsByTurn = new Map();
    rowsByTurn = new Map();
    observationsByTurn = new Map();
    suggestionsByTurn = new Map();
    sparqlByTurn = new Map();
  }

  return {
    get conversation(): ConversationTurn[] {
      return conversation;
    },
    get loading(): boolean {
      return loading;
    },
    get error(): string | null {
      return error;
    },
    get intentByTurn(): Map<string, string> {
      return intentByTurn;
    },
    get clarificationByTurn(): Map<string, string> {
      return clarificationByTurn;
    },
    get limitationByTurn(): Map<string, string> {
      return limitationByTurn;
    },
    get columnsByTurn(): Map<string, ResultColumn[]> {
      return columnsByTurn;
    },
    get rowsByTurn(): Map<string, ResultRow[]> {
      return rowsByTurn;
    },
    get observationsByTurn(): Map<string, string[]> {
      return observationsByTurn;
    },
    get suggestionsByTurn(): Map<string, string[]> {
      return suggestionsByTurn;
    },
    get sparqlByTurn(): Map<string, string> {
      return sparqlByTurn;
    },
    sendMessage,
    selectSuggestion,
    retry,
    clearExploration
  };
}

export const exploration = createExplorationStore();
