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
  HistoryTurn,
  EntityInteraction
} from '$lib/types/exploration';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

function createExplorationStore() {
  let conversation = $state<ConversationTurn[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);
  let headTurnId = $state<string | null>(null);
  let abortController: AbortController | null = null;

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

  function parseSseEvent(raw: string): { event: string; data: any } | null {
    let event = 'message';
    let data = '';

    for (const line of raw.split(/\r?\n/)) {
      if (line.startsWith('event:')) event = line.slice(6).trim();
      if (line.startsWith('data:')) data += line.slice(5).trim();
    }

    if (!data) return null;
    return { event, data: JSON.parse(data) };
  }

  function patchRows(turnId: string, offset: number, incoming: ResultRow[]): void {
    const current = rowsByTurn.get(turnId) || [];
    const next = [...current];
    next.splice(offset, incoming.length, ...incoming);
    rowsByTurn = new Map(rowsByTurn).set(turnId, next);
  }

  async function sendMessage(
    content: string,
    fromTurnId?: string | null,
    interaction?: EntityInteraction
  ): Promise<void> {
    if (!content.trim() || loading) return;

    const parentId = fromTurnId !== undefined ? fromTurnId : headTurnId;

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
      loading: true,
      streaming: true
    };
    conversation = [...conversation, assistantTurn];
    headTurnId = assistantTurn.id;
    loading = true;
    error = null;
    abortController = new AbortController();

    const history = buildHistory();

    try {
      const res = await fetch(`${API_BASE}/api/exploration/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content, history, interaction }),
        signal: abortController.signal
      });

      if (!res.ok || !res.body) {
        throw new Error(`API error: ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let completed = false;

      const handleEvent = (event: string, data: any): void => {
        switch (event) {
          case 'interpretation':
            conversation = conversation.map((t) =>
              t.id === assistantTurn.id ? { ...t, content: data.text } : t
            );
            interpretationByTurn = new Map(interpretationByTurn).set(assistantTurn.id, data.text);
            break;
          case 'sparql':
            sparqlByTurn = new Map(sparqlByTurn).set(assistantTurn.id, data.query);
            break;
          case 'result':
            columnsByTurn = new Map(columnsByTurn).set(assistantTurn.id, data.columns);
            rowsByTurn = new Map(rowsByTurn).set(assistantTurn.id, data.rows);
            break;
          case 'row_questions':
            patchRows(assistantTurn.id, data.offset, data.rows);
            break;
          case 'observations':
            observationsByTurn = new Map(observationsByTurn).set(assistantTurn.id, data.items);
            break;
          case 'suggestions':
            suggestionsByTurn = new Map(suggestionsByTurn).set(assistantTurn.id, data.items);
            break;
          case 'complete':
            completed = true;
            conversation = conversation.map((t) =>
              t.id === assistantTurn.id ? { ...t, loading: false, streaming: false } : t
            );
            break;
          case 'error':
            completed = true;
            const streamMessage = data.message || 'The stream failed.';
            conversation = conversation.map((t) =>
              t.id === assistantTurn.id
                ? { ...t, content: streamMessage, loading: false, streaming: false, error: true }
                : t
            );
            error = streamMessage;
            break;
        }
      };

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split('\n\n');
        buffer = chunks.pop() || '';

        for (const chunk of chunks) {
          const parsed = parseSseEvent(chunk);
          if (parsed) handleEvent(parsed.event, parsed.data);
        }
      }

      if (buffer.trim()) {
        const parsed = parseSseEvent(buffer);
        if (parsed) handleEvent(parsed.event, parsed.data);
      }

      if (!completed) {
        throw new Error('The streaming response ended before completion.');
      }
    } catch (e) {
      if (e instanceof DOMException && e.name === 'AbortError') return;
      const message = e instanceof Error ? e.message : 'Unknown error';
      conversation = conversation.map((t) =>
        t.id === assistantTurn.id
          ? {
              ...t,
              content: `Failed to get response: ${message}`,
              loading: false,
              streaming: false,
              error: true
            }
          : t
      );
      error = message;
    }

    loading = false;
    abortController = null;
  }

  function selectSuggestion(
    suggestion: string,
    fromTurnId?: string | null,
    interaction?: EntityInteraction
  ): void {
    sendMessage(suggestion, fromTurnId, interaction);
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
    abortController?.abort();
    abortController = null;
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
