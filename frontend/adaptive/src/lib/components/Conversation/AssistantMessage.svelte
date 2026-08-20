<script lang="ts">
  import type { ConversationTurn, ResultState, Observation, FollowUpQuestion, Filter } from '$lib/types/exploration';
  import Spinner from '$lib/components/Shared/Spinner.svelte';
  import ExplorationRenderer from '$lib/components/Results/ExplorationRenderer.svelte';
  import FilterBar from '$lib/components/Controls/FilterBar.svelte';
  import ObservationCard from '$lib/components/Insights/ObservationCard.svelte';
  import SuggestionChips from '$lib/components/Insights/SuggestionChips.svelte';
  import QueryToggle from '$lib/components/Insights/QueryToggle.svelte';

  let {
    message,
    result,
    observations,
    suggestions,
    filters,
    sparqlQuery,
    onRemoveFilter,
    onSelectSuggestion
  }: {
    message: ConversationTurn;
    result: ResultState | null;
    observations: Observation[];
    suggestions: FollowUpQuestion[];
    filters: Filter[];
    sparqlQuery?: string;
    onRemoveFilter: (filter: Filter) => void;
    onSelectSuggestion: (suggestion: FollowUpQuestion) => void;
  } = $props();

  function formatTime(date: Date): string {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
</script>

<div class="message assistant" class:error={message.error}>
  <div class="avatar">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>
  </div>

  <div class="content">
    <div class="message-header">
      <span class="role">Assistant</span>
      <span class="time">{formatTime(message.timestamp)}</span>
    </div>

    <div class="message-body">
      {#if message.loading}
        <div class="loading">
          <Spinner size={14} />
          <span>Thinking about the question...</span>
        </div>
      {:else if message.content && !sparqlQuery}
        <p>{message.content}</p>
      {/if}

      {#if filters.length > 0}
        <FilterBar {filters} onRemove={onRemoveFilter} />
      {/if}

      {#if result && !message.loading && !message.error}
        <ExplorationRenderer {result} />
      {/if}

      {#if sparqlQuery && !message.loading && !message.error}
        <QueryToggle naturalLanguage={message.content} {sparqlQuery} />
      {/if}

      {#if observations.length > 0 && !message.loading}
        {#each observations as observation (observation.id)}
          <ObservationCard {observation} />
        {/each}
      {/if}

      {#if suggestions.length > 0 && !message.loading}
        <SuggestionChips {suggestions} onSelect={onSelectSuggestion} />
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
    color: var(--text-secondary);
  }

  .content {
    max-width: 80%;
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

  .loading {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-secondary);
    font-size: 0.8125rem;
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
    .content {
      max-width: 90%;
    }

    .message {
      padding: 0.625rem 0.75rem;
    }
  }
</style>
