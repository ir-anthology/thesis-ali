import type { Facet, Filter, FacetRow, Observation, FollowUpQuestion } from '$lib/types/exploration';

// Mock exploration API functions
// These simulate future backend integration

export interface ExplorationResult {
  targetFacet: Facet;
  filters: Filter[];
  rows: FacetRow[];
  observations: Observation[];
  followUpQuestions: FollowUpQuestion[];
}

export interface InteractionRequest {
  interaction: 'cell_click' | 'filter_remove' | 'sort';
  facet?: Facet;
  value?: string | number;
  currentTargetFacet?: Facet;
  filters?: Filter[];
}

export interface InteractionResult {
  targetFacet: Facet;
  filters: Filter[];
  rows: FacetRow[];
  generatedPrompt?: string;
}

const API_BASE = 'http://127.0.0.1:8000';

export interface ChatResponse {
  type: 'sparql' | 'table';
  content: string;
}

export interface HealthResponse {
  status: string;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Legacy chat API (kept for reference)
export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message })
  });

  if (!response.ok) {
    throw new ApiError(
      `API request failed: ${response.statusText}`,
      response.status
    );
  }

  return await response.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) return false;
    const data: HealthResponse = await response.json();
    return data.status === 'ok';
  } catch {
    return false;
  }
}

// Mock exploration functions (no backend needed for now)
export async function exploreQuestion(_question: string): Promise<ExplorationResult> {
  await new Promise(r => setTimeout(r, 2300));
  return {
    targetFacet: 'author',
    filters: [],
    rows: [],
    observations: [],
    followUpQuestions: []
  };
}

export async function tableInteraction(_interaction: InteractionRequest): Promise<InteractionResult> {
  await new Promise(r => setTimeout(r, 300));
  return {
    targetFacet: 'author',
    filters: [],
    rows: []
  };
}
