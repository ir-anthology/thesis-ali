<script lang="ts">
  import type { ConversationTurn } from '$lib/types/exploration';

  let { message }: { message: ConversationTurn } = $props();

  function formatTime(date: Date): string {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
</script>

<div class="message user">
  <div class="avatar">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
      <circle cx="12" cy="7" r="4"></circle>
    </svg>
  </div>
  <div class="content">
    <div class="message-header">
      <span class="role">You</span>
      <span class="time">{formatTime(message.timestamp)}</span>
    </div>
    <div class="message-body">
      <p>{message.content}</p>
    </div>
  </div>
</div>

<style>
  .message {
    display: flex;
    gap: 0.625rem;
    padding: 0.75rem 1rem;
    animation: fadeIn 0.2s ease-out;
    flex-direction: row-reverse;
  }

  .avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    background-color: var(--accent);
    color: white;
  }

  .content {
    max-width: 70%;
    padding: 0.625rem 0.875rem;
    background-color: var(--user-bubble);
    border-radius: 12px 12px 2px 12px;
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

  @media (max-width: 640px) {
    .content {
      max-width: 85%;
    }

    .message {
      padding: 0.625rem 0.75rem;
    }
  }
</style>
