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
  EntityInteraction,
  AnalyticsInteraction,
  CellQuestionContext,
  StreamStage
} from '$lib/types/exploration';
import { analyticsHeaders } from '$lib/analytics';

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

  async function sendMessage(
    content: string,
    fromTurnId?: string | null,
    interaction?: EntityInteraction,
    analyticsInteraction?: AnalyticsInteraction
  ): Promise<void> {
    if (!content.trim() || loading) return;

    await createMessageBranch(content, fromTurnId !== undefined ? fromTurnId : headTurnId, {
      branchSourceId: fromTurnId && fromTurnId !== headTurnId ? fromTurnId : undefined,
      interaction,
      analyticsInteraction: analyticsInteraction || {
        type: 'typed',
        from_turn_id: fromTurnId ?? null
      }
    });
  }

  async function createMessageBranch(
    content: string,
    parentId: string | null,
    options: {
      branchSourceId?: string;
      interaction?: EntityInteraction;
      analyticsInteraction?: AnalyticsInteraction;
    } = {},
    existingUserTurnId?: string
  ): Promise<void> {
    if (!content.trim() || (loading && !existingUserTurnId)) return;

    if (options.branchSourceId && !existingUserTurnId) {
      conversation = conversation.map(t =>
        t.id === options.branchSourceId ? { ...t, branchCount: (t.branchCount || 0) + 1 } : t
      );
    }

    const userTurn = existingUserTurnId
      ? conversation.find((turn) => turn.id === existingUserTurnId)
      : undefined;
    if (existingUserTurnId && (!userTurn || userTurn.role !== 'user')) return;

    const resolvedUserTurn: ConversationTurn = userTurn || {
      id: generateId(),
      parentId,
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    };
    if (userTurn) {
      conversation = conversation.map((turn) =>
        turn.id === userTurn.id
          ? { ...turn, content: content.trim(), pending: false, pendingMessage: undefined }
          : turn
      );
    } else {
      conversation = [...conversation, resolvedUserTurn];
    }
    headTurnId = resolvedUserTurn.id;

    const assistantTurn: ConversationTurn = {
      id: generateId(),
      parentId: resolvedUserTurn.id,
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
        headers: {
          'Content-Type': 'application/json',
          ...analyticsHeaders()
        },
        body: JSON.stringify({
          message: content,
          history,
          interaction: options.interaction,
          analytics_interaction: options.analyticsInteraction
        }),
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
          case 'stage':
            conversation = conversation.map((t) =>
              t.id === assistantTurn.id
                ? {
                    ...t,
                    streaming: true,
                    streamingStage: data.stage as StreamStage,
                    streamingMessage: data.message
                  }
                : t
            );
            break;
          case 'sparql':
            sparqlByTurn = new Map(sparqlByTurn).set(assistantTurn.id, data.query);
            break;
          case 'result':
            columnsByTurn = new Map(columnsByTurn).set(assistantTurn.id, data.columns);
            rowsByTurn = new Map(rowsByTurn).set(assistantTurn.id, data.rows);
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
              t.id === assistantTurn.id
                ? {
                    ...t,
                    loading: false,
                    streaming: false,
                    streamingStage: undefined,
                    streamingMessage: undefined
                  }
                : t
            );
            break;
          case 'error':
            completed = true;
            const streamMessage = data.message || 'The stream failed.';
            conversation = conversation.map((t) =>
              t.id === assistantTurn.id
                ? {
                    ...t,
                    content: streamMessage,
                    loading: false,
                    streaming: false,
                    streamingStage: undefined,
                    streamingMessage: undefined,
                    error: true
                  }
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
              streamingStage: undefined,
              streamingMessage: undefined,
              error: true
            }
          : t
      );
      error = message;
    }

    loading = false;
    abortController = null;
  }

  async function selectCell(
    context: CellQuestionContext,
    fromTurnId: string,
    interaction?: EntityInteraction
  ): Promise<void> {
    if (loading) return;

    const userTurn: ConversationTurn = {
      id: generateId(),
      parentId: fromTurnId,
      role: 'user',
      content: '',
      timestamp: new Date(),
      pending: true,
      pendingMessage: 'Formulating follow-up questions…'
    };
    if (fromTurnId !== headTurnId) {
      conversation = conversation.map((turn) =>
        turn.id === fromTurnId
          ? { ...turn, branchCount: (turn.branchCount || 0) + 1 }
          : turn
      );
    }
    conversation = [...conversation, userTurn];
    headTurnId = userTurn.id;
    loading = true;
    error = null;

    try {
      const res = await fetch(`${API_BASE}/api/cell-question`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...analyticsHeaders()
        },
        body: JSON.stringify(context)
      });
      if (!res.ok) throw new Error(`Cell-question API error: ${res.status}`);

      const data: { question?: string } = await res.json();
      if (!data.question?.trim()) throw new Error('The backend returned no follow-up question.');

      await createMessageBranch(
        data.question,
        fromTurnId,
        {
          interaction,
          analyticsInteraction: {
            type: 'cell_click',
            from_turn_id: fromTurnId,
            details: {
              column: context.column,
              value: context.value,
              ...(interaction?.entity_id ? { entity_id: interaction.entity_id } : {}),
              ...(interaction?.entity_type ? { entity_type: interaction.entity_type } : {})
            }
          }
        },
        userTurn.id
      );
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Unknown error';
      conversation = conversation.map((turn) =>
        turn.id === userTurn.id
          ? {
              ...turn,
              content: `Failed to formulate follow-up question: ${message}`,
              pending: false,
              pendingMessage: undefined,
              error: true
            }
          : turn
      );
      error = message;
      loading = false;
    }
  }

  function editUserPrompt(turnId: string, editedContent: string): void {
    const originalTurn = conversation.find((t) => t.id === turnId);
    const content = editedContent.trim();

    if (!originalTurn || originalTurn.role !== 'user' || !content || content === originalTurn.content || loading) {
      return;
    }

    createMessageBranch(content, originalTurn.parentId, {
      branchSourceId: originalTurn.id,
      analyticsInteraction: {
        type: 'edit',
        from_turn_id: originalTurn.id,
        details: { edited_turn_id: originalTurn.id }
      }
    });
  }

  function selectSuggestion(
    suggestion: string,
    fromTurnId?: string | null,
    interaction?: EntityInteraction,
    analyticsInteraction?: AnalyticsInteraction
  ): void {
    sendMessage(
      suggestion,
      fromTurnId,
      interaction,
      analyticsInteraction || {
        type: 'suggestion_click',
        from_turn_id: fromTurnId ?? null,
        details: { suggestion }
      }
    );
  }

  function retry(): void {
    const activePath = getActivePath();
    const lastUserTurn = [...activePath].reverse().find((t) => t.role === 'user');
    if (lastUserTurn) {
      conversation = conversation.filter((t) => !t.loading && !(t.role === 'assistant' && t.error));
      headTurnId = lastUserTurn.parentId;
      sendMessage(
        lastUserTurn.content,
        lastUserTurn.parentId ?? undefined,
        undefined,
        {
          type: 'retry',
          from_turn_id: lastUserTurn.parentId,
          details: { retried_turn_id: lastUserTurn.id }
        }
      );
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
    editUserPrompt,
    selectSuggestion,
    selectCell,
    retry,
    clearExploration
  };
}

export const exploration = createExplorationStore();
