<script lang="ts">
  import type { ConversationTurn, EntityInteraction, ResultColumn, ResultRow } from '$lib/types/exploration';
  import Spinner from '$lib/components/Shared/Spinner.svelte';
  import ResultBox from '$lib/components/Results/ResultBox.svelte';
  import ObservationCard from '$lib/components/Insights/ObservationCard.svelte';
  import SuggestionChips from '$lib/components/Insights/SuggestionChips.svelte';

  let {
    message,
    interpretation,
    columns,
    rows,
    observations,
    suggestions,
    sparqlQuery,
    disabled = false,
    onSelectSuggestion,
    onCellClick
  }: {
    message: ConversationTurn;
    interpretation?: string;
    columns?: ResultColumn[];
    rows?: ResultRow[];
    observations?: string[];
    suggestions?: string[];
    sparqlQuery?: string;
    disabled?: boolean;
    onSelectSuggestion: (suggestion: string) => void;
    onCellClick?: (question: string, interaction?: EntityInteraction) => void;
  } = $props();

  function formatTime(date: Date): string {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
</script>

<div class="message assistant" class:error={message.error}>
  <div class="avatar">
    <span class="avatar-text">IR</span>
  </div>

  <div class="content">
    <div class="message-header">
      <span class="role">IR Anthology</span>
      <span class="time">{formatTime(message.timestamp)}</span>
    </div>

    <div class="message-body">
      {#if interpretation}
        <p class="interpretation-text">{interpretation}</p>
      {/if}

      {#if message.streaming}
        <div class="streaming-status">
          <Spinner size={12} />
          <span>{message.streamingMessage}</span>
        </div>
      {/if}

      {#if columns && rows && !message.error}
        <ResultBox {columns} {rows} {sparqlQuery} {onCellClick} {disabled} />
      {/if}

      {#if observations && observations.length > 0}
        {#each observations as text, i (i)}
          <ObservationCard {text} />
        {/each}
      {/if}

      {#if suggestions && suggestions.length > 0}
        <SuggestionChips {suggestions} onSelect={onSelectSuggestion} {disabled} />
      {/if}

      {#if message.error}
        <p class="error-text">Please try again or rephrase your question.</p>
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
    background-color: var(--bg-tertiary);
  }

  .avatar-text {
    font-size: 0.75rem;
    font-weight: 700;
    font-family: 'Georgia', 'Times New Roman', serif;
    color: rgb(149, 21, 21);
    letter-spacing: -0.02em;
  }

  .content {
    flex: 1;
    min-width: 0;
    max-width: 100%;
    padding: 0.625rem 0.875rem;
    background-color: var(--assistant-bubble);
    border-radius: 12px 12px 12px 2px;
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

  .interpretation-text {
    margin-bottom: 0.75rem;
  }

  .streaming-status {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    color: var(--text-muted);
    font-size: 0.75rem;
    margin-top: 0.5rem;
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

  @media (max-width: 640px) {
    .message {
      padding: 0.625rem 0.75rem;
    }
  }
</style>
