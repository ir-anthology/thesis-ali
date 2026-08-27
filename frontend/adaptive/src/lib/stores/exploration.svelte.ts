/**
 * Exploration Store
 *
 * This module manages the entire exploration state using Svelte 5 runes.
 * It provides a reactive store that handles:
 * - Conversation history (user and assistant turns)
 * - Per-turn response data (columns, rows, observations, suggestions)
 *
 * The store uses mock data for demonstration purposes.
 * In production, it would integrate with a backend API.
 */

import type {
  ConversationTurn,
  ResultColumn,
  ResultRow,
  ExplorationResponse,
  HistoryTurn
} from '$lib/types/exploration';
import { mockResponses } from '$lib/data/mock-responses';

function createExplorationStore() {
  let conversation = $state<ConversationTurn[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);

  let columnsByTurn = $state<Map<string, ResultColumn[]>>(new Map());
  let rowsByTurn = $state<Map<string, ResultRow[]>>(new Map());
  let observationsByTurn = $state<Map<string, string[]>>(new Map());
  let suggestionsByTurn = $state<Map<string, string[]>>(new Map());
  let sparqlByTurn = $state<Map<string, string>>(new Map());
  let responseTextByTurn = $state<Map<string, string>>(new Map());

  function generateId(): string {
    return crypto.randomUUID();
  }

  function buildHistory(): HistoryTurn[] {
    return conversation.map((turn) => {
      if (turn.role === 'user') {
        return { role: 'user', content: turn.content };
      }
      return {
        role: 'assistant',
        content: turn.content,
        response_text: responseTextByTurn.get(turn.id),
        columns: columnsByTurn.get(turn.id),
        rows: rowsByTurn.get(turn.id),
        observations: observationsByTurn.get(turn.id),
        suggestions: suggestionsByTurn.get(turn.id),
        sparql_query: sparqlByTurn.get(turn.id)
      };
    });
  }

  function findMockResponse(message: string): ExplorationResponse | null {
    const lower = message.toLowerCase();

    if (lower.includes('prolific') || lower.includes('most authors')) {
      return mockResponses['prolific-authors'];
    }
    if (lower.includes('last five') || lower.includes('last 5')) {
      return mockResponses['filtered-years'];
    }
    if (lower.includes('venue') || lower.includes('publish in')) {
      return mockResponses['venues'];
    }
    if (lower.includes('changed over time') || lower.includes('how has')) {
      return mockResponses['timeline'];
    }
    if (lower.includes('compare')) {
      return mockResponses['comparison'];
    }
    if (lower.includes('why') && lower.includes('sigir')) {
      return mockResponses['why-sigir'];
    }

    return mockResponses['unsupported'];
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

    await new Promise((resolve) => setTimeout(resolve, 800 + Math.random() * 700));

    const response = findMockResponse(content);

    if (response) {
      conversation = conversation.map((t) =>
        t.id === assistantTurn.id
          ? { ...t, content: response.response_text, loading: false }
          : t
      );

      responseTextByTurn = new Map(responseTextByTurn).set(assistantTurn.id, response.response_text);

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
    } else {
      conversation = conversation.map((t) =>
        t.id === assistantTurn.id
          ? {
              ...t,
              content: 'Sorry, I encountered an error. Please try again.',
              loading: false,
              error: true
            }
          : t
      );
      error = 'Failed to get response';
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
    columnsByTurn = new Map();
    rowsByTurn = new Map();
    observationsByTurn = new Map();
    suggestionsByTurn = new Map();
    sparqlByTurn = new Map();
    responseTextByTurn = new Map();
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
    get responseTextByTurn(): Map<string, string> {
      return responseTextByTurn;
    },
    sendMessage,
    selectSuggestion,
    retry,
    clearExploration
  };
}

export const exploration = createExplorationStore();
