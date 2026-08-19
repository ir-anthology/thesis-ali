<script>
  import SparqlCodeBlock from './SparqlCodeBlock.svelte';
  import TableResult from './TableResult.svelte';

  let { message, onExecute } = $props();

  function formatTime(date) {
    return new Date(date).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<div class="message {message.role}" class:error={message.error}>
  <div class="avatar">
    {#if message.role === 'user'}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
    {:else}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      </svg>
    {/if}
  </div>

  <div class="content">
    <div class="message-header">
      <span class="role">{message.role === 'user' ? 'You' : 'Assistant'}</span>
      <span class="time">{formatTime(message.timestamp)}</span>
    </div>

    <div class="message-body">
      {#if message.loading}
        <div class="loading">
          <div class="spinner"></div>
          <span>Processing...</span>
        </div>
      {:else if message.content}
        <p>{message.content}</p>
      {/if}

      {#if message.sparql}
        <SparqlCodeBlock code={message.sparql} {onExecute} />
      {/if}

      {#if message.table}
        <TableResult table={message.table} />
      {/if}

      {#if message.error}
        <p class="error-text">Please check if the backend server is running.</p>
      {/if}
    </div>
  </div>
</div>

<style>
  .message {
    display: flex;
    gap: 0.625rem;
    padding: 0.75rem 1rem;
    animation: fadeIn 0.2s ease-out;
  }

  .message.user {
    flex-direction: row-reverse;
  }

  .message.user .content {
    background-color: var(--user-bubble);
    border-radius: 12px 12px 2px 12px;
  }

  .message.assistant .content {
    background-color: var(--assistant-bubble);
    border-radius: 12px 12px 12px 2px;
  }

  .message.error .content {
    border: 1px solid var(--error);
  }

  .avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    color: var(--text-secondary);
  }

  .message.user .avatar {
    background-color: var(--accent);
    color: white;
  }

  .message.assistant .avatar {
    background-color: var(--bg-tertiary);
    color: var(--text-secondary);
  }

  .content {
    max-width: 70%;
    padding: 0.625rem 0.875rem;
  }

  .message-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
  }

  .role {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  .time {
    font-size: 0.6875rem;
    color: var(--text-muted);
  }

  .message-body {
    color: var(--text-primary);
    line-height: 1.5;
    font-size: 0.875rem;
  }

  .message-body p {
    margin: 0;
  }

  .loading {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-secondary);
    font-size: 0.8125rem;
  }

  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  .error-text {
    color: var(--error);
    font-size: 0.8125rem;
    margin-top: 0.5rem;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(6px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  @media (max-width: 640px) {
    .content {
      max-width: 85%;
    }

    .message {
      padding: 0.625rem 0.75rem;
    }
  }
</style>
