import type {
  ConversationTurn,
  Filter,
  Facet,
  SortState,
  ResultState,
  Observation,
  FollowUpQuestion
} from '$lib/types/exploration';

const STORAGE_KEY = 'scholarly-explorer-state';

export interface PersistedState {
  conversation: SerializedConversationTurn[];
  filters: Filter[];
  targetFacet: Facet | null;
  sorting: SortState | null;
  result: ResultState | null;
  observations: Observation[];
  suggestions: FollowUpQuestion[];
}

interface SerializedConversationTurn {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  loading?: boolean;
  error?: boolean;
}

export function serializeConversation(turns: ConversationTurn[]): SerializedConversationTurn[] {
  return turns.map((turn) => ({
    id: turn.id,
    role: turn.role,
    content: turn.content,
    timestamp: turn.timestamp.toISOString(),
    loading: turn.loading,
    error: turn.error
  }));
}

export function deserializeConversation(
  turns: SerializedConversationTurn[]
): ConversationTurn[] {
  return turns.map((turn) => ({
    id: turn.id,
    role: turn.role,
    content: turn.content,
    timestamp: new Date(turn.timestamp),
    loading: turn.loading,
    error: turn.error
  }));
}

export function saveToSessionStorage(state: PersistedState): void {
  try {
    const serialized = {
      ...state,
      conversation: serializeConversation(state.conversation)
    };
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(serialized));
  } catch {
    console.warn('Failed to save state to sessionStorage');
  }
}

export function loadFromSessionStorage(): PersistedState | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;

    const parsed = JSON.parse(raw);
    return {
      ...parsed,
      conversation: deserializeConversation(parsed.conversation || [])
    };
  } catch {
    console.warn('Failed to load state from sessionStorage');
    return null;
  }
}

export function clearSessionStorage(): void {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    console.warn('Failed to clear sessionStorage');
  }
}

export function encodeStateToUrl(params: {
  q?: string;
  facet?: Facet;
  filters?: Filter[];
}): URLSearchParams {
  const searchParams = new URLSearchParams();

  if (params.q) {
    searchParams.set('q', params.q);
  }
  if (params.facet) {
    searchParams.set('facet', params.facet);
  }
  if (params.filters && params.filters.length > 0) {
    searchParams.set('filters', JSON.stringify(params.filters));
  }

  return searchParams;
}

export function decodeStateFromUrl(searchParams: URLSearchParams): {
  q?: string;
  facet?: Facet;
  filters?: Filter[];
} {
  const result: {
    q?: string;
    facet?: Facet;
    filters?: Filter[];
  } = {};

  const q = searchParams.get('q');
  if (q) {
    result.q = q;
  }

  const facet = searchParams.get('facet');
  if (facet && isValidFacet(facet)) {
    result.facet = facet;
  }

  const filtersStr = searchParams.get('filters');
  if (filtersStr) {
    try {
      const filters = JSON.parse(filtersStr);
      if (Array.isArray(filters)) {
        result.filters = filters;
      }
    } catch {
      console.warn('Failed to parse filters from URL');
    }
  }

  return result;
}

function isValidFacet(value: string): value is Facet {
  return ['author', 'venue', 'year', 'publication'].includes(value);
}
