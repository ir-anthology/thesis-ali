import type {
  ConversationTurn,
  Facet,
  SortState,
  ResultState,
  Observation,
  FollowUpQuestion,
  ResponseStatus
} from '$lib/types/exploration';

const STORAGE_KEY = 'ir-anthology-chat-state';

export interface PersistedState {
  conversation: ConversationTurn[];
  targetFacet: Facet | null;
  sorting: SortState | null;
  result: ResultState | null;
  observations: Observation[];
  suggestions: FollowUpQuestion[];
  resultsByTurn?: Record<string, ResultState>;
  observationsByTurn?: Record<string, Observation[]>;
  suggestionsByTurn?: Record<string, FollowUpQuestion[]>;
  sparqlByTurn?: Record<string, string>;
  statusByTurn?: Record<string, ResponseStatus>;
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

export function saveToSessionStorage(state: {
  conversation: ConversationTurn[];
  targetFacet: Facet | null;
  sorting: SortState | null;
  result: ResultState | null;
  observations: Observation[];
  suggestions: FollowUpQuestion[];
  resultsByTurn?: Record<string, ResultState>;
  observationsByTurn?: Record<string, Observation[]>;
  suggestionsByTurn?: Record<string, FollowUpQuestion[]>;
  sparqlByTurn?: Record<string, string>;
  statusByTurn?: Record<string, ResponseStatus>;
}): void {
  try {
    const serialized = {
      conversation: serializeConversation(state.conversation),
      targetFacet: state.targetFacet,
      sorting: state.sorting,
      result: state.result,
      observations: state.observations,
      suggestions: state.suggestions,
      resultsByTurn: state.resultsByTurn,
      observationsByTurn: state.observationsByTurn,
      suggestionsByTurn: state.suggestionsByTurn,
      sparqlByTurn: state.sparqlByTurn,
      statusByTurn: state.statusByTurn
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
      conversation: deserializeConversation(parsed.conversation || []),
      targetFacet: parsed.targetFacet || null,
      sorting: parsed.sorting || null,
      result: parsed.result || null,
      observations: parsed.observations || [],
      suggestions: parsed.suggestions || [],
      resultsByTurn: parsed.resultsByTurn || {},
      observationsByTurn: parsed.observationsByTurn || {},
      suggestionsByTurn: parsed.suggestionsByTurn || {},
      sparqlByTurn: parsed.sparqlByTurn || {},
      statusByTurn: parsed.statusByTurn || {}
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
}): URLSearchParams {
  const searchParams = new URLSearchParams();

  if (params.q) {
    searchParams.set('q', params.q);
  }
  if (params.facet) {
    searchParams.set('facet', params.facet);
  }

  return searchParams;
}

export function decodeStateFromUrl(searchParams: URLSearchParams): {
  q?: string;
  facet?: Facet;
} {
  const result: {
    q?: string;
    facet?: Facet;
  } = {};

  const q = searchParams.get('q');
  if (q) {
    result.q = q;
  }

  const facet = searchParams.get('facet');
  if (facet && isValidFacet(facet)) {
    result.facet = facet;
  }

  return result;
}

function isValidFacet(value: string): value is Facet {
  return ['author', 'venue', 'year', 'publication'].includes(value);
}
