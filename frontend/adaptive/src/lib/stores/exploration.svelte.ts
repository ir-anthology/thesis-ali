/**
 * Exploration Store
 *
 * This module manages the entire exploration state using Svelte 5 runes.
 * It provides a reactive store that handles:
 * - Conversation history (user and assistant turns)
 * - Active filters and sorting
 * - Current result data and visualizations
 * - LLM-generated observations and follow-up suggestions
 * - Session persistence for state recovery
 *
 * The store uses mock data for demonstration purposes.
 * In production, it would integrate with a backend API.
 */

import type {
  ConversationTurn,
  Filter,
  Facet,
  SortState,
  ResultState,
  Observation,
  FollowUpQuestion,
  Entity,
  ExplorationResponse
} from '$lib/types/exploration';
import { mockResponses } from '$lib/data/mock-responses';
import {
  saveToSessionStorage,
  loadFromSessionStorage,
  clearSessionStorage
} from '$lib/utils/persistence';

function createExplorationStore() {
  let conversation = $state<ConversationTurn[]>([]);
  let filters = $state<Filter[]>([]);
  let targetFacet = $state<Facet | null>(null);
  let sorting = $state<SortState | null>(null);
  let result = $state<ResultState | null>(null);
  let observations = $state<Observation[]>([]);
  let suggestions = $state<FollowUpQuestion[]>([]);
  let selectedEntities = $state<Entity[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);

  function generateId(): string {
    return crypto.randomUUID();
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

    await new Promise((resolve) => setTimeout(resolve, 800 + Math.random() * 700));

    const response = findMockResponse(content);

    if (response) {
      conversation = conversation.map((t) =>
        t.id === assistantTurn.id
          ? { ...t, content: response.result.title || 'Here are the results:', loading: false }
          : t
      );
      result = response.result;
      observations = response.interpretation.observations;
      suggestions = response.interpretation.suggestions;

      if (response.exploration.targetFacet) {
        targetFacet = response.exploration.targetFacet;
      }
      if (response.exploration.filters.length > 0) {
        filters = response.exploration.filters;
      }
      if (response.exploration.sort) {
        sorting = response.exploration.sort;
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
    saveState();
  }

  function applyFilter(filter: Filter): void {
    if (!filters.find((f) => f.facet === filter.facet && f.value === filter.value)) {
      filters = [...filters, filter];
    }
  }

  function removeFilter(filter: Filter): void {
    filters = filters.filter((f) => !(f.facet === filter.facet && f.value === filter.value));
  }

  function setSorting(sort: SortState): void {
    sorting = sort;
  }

  function setTargetFacet(facet: Facet): void {
    targetFacet = facet;
  }

  function selectEntity(entity: Entity): void {
    if (!selectedEntities.find((e) => e.id === entity.id)) {
      selectedEntities = [...selectedEntities, entity];
    }
  }

  function clearSelection(): void {
    selectedEntities = [];
  }

  function selectSuggestion(suggestion: FollowUpQuestion): void {
    sendMessage(suggestion.text);
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
    filters = [];
    targetFacet = null;
    sorting = null;
    result = null;
    observations = [];
    suggestions = [];
    selectedEntities = [];
    loading = false;
    error = null;
    clearSessionStorage();
  }

  function saveState(): void {
    saveToSessionStorage({
      conversation,
      filters,
      targetFacet,
      sorting,
      result,
      observations,
      suggestions
    });
  }

  function loadState(): boolean {
    const saved = loadFromSessionStorage();
    if (!saved) return false;

    conversation = saved.conversation;
    filters = saved.filters;
    targetFacet = saved.targetFacet;
    sorting = saved.sorting;
    result = saved.result;
    observations = saved.observations;
    suggestions = saved.suggestions;
    loading = false;
    error = null;

    return true;
  }

  return {
    get conversation(): ConversationTurn[] {
      return conversation;
    },
    get filters(): Filter[] {
      return filters;
    },
    get targetFacet(): Facet | null {
      return targetFacet;
    },
    get sorting(): SortState | null {
      return sorting;
    },
    get result(): ResultState | null {
      return result;
    },
    get observations(): Observation[] {
      return observations;
    },
    get suggestions(): FollowUpQuestion[] {
      return suggestions;
    },
    get selectedEntities(): Entity[] {
      return selectedEntities;
    },
    get loading(): boolean {
      return loading;
    },
    get error(): string | null {
      return error;
    },
    sendMessage,
    applyFilter,
    removeFilter,
    setSorting,
    setTargetFacet,
    selectEntity,
    clearSelection,
    selectSuggestion,
    retry,
    clearExploration,
    saveState,
    loadState
  };
}

export const exploration = createExplorationStore();
