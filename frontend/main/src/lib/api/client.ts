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
