/**
 * Exploration Store
 *
 * This module manages the entire exploration state using Svelte 5 runes.
 * It provides a reactive store that handles:
 * - Conversation history (user and assistant turns)
 * - Per-turn response data (columns, rows, observations, suggestions)
 * - Per-turn interpretation
 *
 * The store communicates with the backend API (configurable via VITE_API_BASE).
 */

import type {
  ConversationTurn,
  ResultColumn,
  ResultRow,
  ExplorationResponse,
  HistoryTurn
} from '$lib/types/exploration';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

function createExplorationStore() {
  let conversation = $state<ConversationTurn[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);
  let headTurnId = $state<string | null>(null);

  let interpretationByTurn = $state<Map<string, string>>(new Map());
  let columnsByTurn = $state<Map<string, ResultColumn[]>>(new Map());
  let rowsByTurn = $state<Map<string, ResultRow[]>>(new Map());
  let observationsByTurn = $state<Map<string, string[]>>(new Map());
  let suggestionsByTurn = $state<Map<string, string[]>>(new Map());
  let sparqlByTurn = $state<Map<string, string>>(new Map());

  function generateId(): string {
    return crypto.randomUUID();
  }

  function getActivePath(): ConversationTurn[] {
    const path: ConversationTurn[] = [];
    let currentId = headTurnId;
    while (currentId) {
      const turn = conversation.find(t => t.id === currentId);
      if (!turn) break;
      path.unshift(turn);
      currentId = turn.parentId;
    }
    return path;
  }

  function buildHistory(): HistoryTurn[] {
    const activePath = getActivePath();
    return activePath.filter(turn => !turn.loading).map((turn) => {
      if (turn.role === 'user') {
        return { role: 'user', content: turn.content };
      }
      return {
        role: 'assistant',
        content: turn.content,
        interpretation: interpretationByTurn.get(turn.id),
        columns: columnsByTurn.get(turn.id),
        rows: rowsByTurn.get(turn.id),
        observations: observationsByTurn.get(turn.id),
        suggestions: suggestionsByTurn.get(turn.id),
        sparql_query: sparqlByTurn.get(turn.id)
      };
    });
  }

  async function sendMessage(content: string, fromTurnId?: string): Promise<void> {
    if (!content.trim() || loading) return;

    const parentId = fromTurnId ?? headTurnId;

    if (fromTurnId && fromTurnId !== headTurnId) {
      conversation = conversation.map(t =>
        t.id === fromTurnId ? { ...t, branchCount: (t.branchCount || 0) + 1 } : t
      );
    }

    const userTurn: ConversationTurn = {
      id: generateId(),
      parentId,
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    };
    conversation = [...conversation, userTurn];
    headTurnId = userTurn.id;

    const assistantTurn: ConversationTurn = {
      id: generateId(),
      parentId: userTurn.id,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      loading: true
    };
    conversation = [...conversation, assistantTurn];
    headTurnId = assistantTurn.id;
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

      const displayText = response.interpretation || '';

      conversation = conversation.map((t) =>
        t.id === assistantTurn.id
          ? { ...t, content: displayText, loading: false }
          : t
      );

      if (response.interpretation) {
        interpretationByTurn = new Map(interpretationByTurn).set(assistantTurn.id, response.interpretation);
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

  function selectSuggestion(suggestion: string, fromTurnId?: string): void {
    sendMessage(suggestion, fromTurnId);
  }

  function retry(): void {
    const activePath = getActivePath();
    const lastUserTurn = [...activePath].reverse().find((t) => t.role === 'user');
    if (lastUserTurn) {
      conversation = conversation.filter((t) => !t.loading && !(t.role === 'assistant' && t.error));
      headTurnId = lastUserTurn.parentId;
      sendMessage(lastUserTurn.content, lastUserTurn.parentId ?? undefined);
    }
  }

  function clearExploration(): void {
    conversation = [];
    headTurnId = null;
    loading = false;
    error = null;
    interpretationByTurn = new Map();
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
    get headTurnId(): string | null {
      return headTurnId;
    },
    get interpretationByTurn(): Map<string, string> {
      return interpretationByTurn;
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
    getActivePath,
    sendMessage,
    selectSuggestion,
    retry,
    clearExploration
  };
}

export const exploration = createExplorationStore();
