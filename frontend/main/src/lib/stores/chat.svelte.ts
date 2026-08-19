import { sendChatMessage } from '$lib/api/client';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sparql?: string;
  table?: string;
  timestamp: Date;
  loading?: boolean;
  error?: boolean;
}

function createChatStore() {
  let messages = $state<Message[]>([]);
  let isLoading = $state(false);

  function generateId(): string {
    return crypto.randomUUID();
  }

  async function sendMessage(content: string): Promise<void> {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    };

    messages = [...messages, userMessage];
    isLoading = true;

    const assistantMessage: Message = {
      id: generateId(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      loading: true
    };

    messages = [...messages, assistantMessage];

    try {
      const response = await sendChatMessage(content.trim());

      if (response.type === 'sparql') {
        messages = messages.map((m) =>
          m.id === assistantMessage.id
            ? {
                ...m,
                sparql: response.content,
                content: 'Here is your SPARQL query:',
                loading: false
              }
            : m
        );
      } else if (response.type === 'table') {
        messages = messages.map((m) =>
          m.id === assistantMessage.id
            ? {
                ...m,
                table: response.content,
                content: 'Here are the query results:',
                loading: false
              }
            : m
        );
      } else {
        messages = messages.map((m) =>
          m.id === assistantMessage.id
            ? {
                ...m,
                content: response.content || 'An unexpected error occurred.',
                loading: false,
                error: true
              }
            : m
        );
      }
    } catch (error) {
      messages = messages.map((m) =>
        m.id === assistantMessage.id
          ? {
              ...m,
              content: 'Sorry, an error occurred. Please try again.',
              loading: false,
              error: true
            }
          : m
      );
    } finally {
      isLoading = false;
    }
  }

  function clearMessages(): void {
    messages = [];
  }

  return {
    get messages(): Message[] {
      return messages;
    },
    get isLoading(): boolean {
      return isLoading;
    },
    sendMessage,
    clearMessages
  };
}

export const chatStore = createChatStore();
