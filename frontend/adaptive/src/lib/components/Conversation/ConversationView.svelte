<script lang="ts">
  import type { ConversationTurn, ResultState, Observation, FollowUpQuestion, Filter } from '$lib/types/exploration';
  import UserMessage from './UserMessage.svelte';
  import AssistantMessage from './AssistantMessage.svelte';
  import EmptyState from '$lib/components/Shared/EmptyState.svelte';

  let {
    conversation,
    results,
    observations,
    suggestions,
    filtersByTurn,
    onRemoveFilter,
    onSelectSuggestion
  }: {
    conversation: ConversationTurn[];
    results: Map<string, ResultState>;
    observations: Map<string, Observation[]>;
    suggestions: Map<string, FollowUpQuestion[]>;
    filtersByTurn: Map<string, Filter[]>;
    onRemoveFilter: (filter: Filter) => void;
    onSelectSuggestion: (suggestion: FollowUpQuestion) => void;
  } = $props();

  let container: HTMLDivElement | undefined = $state();

  $effect(() => {
    conversation.length;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  });
</script>

<div
  class="conversation-container"
  bind:this={container}
  role="log"
  aria-label="Conversation history"
  aria-live="polite"
  aria-relevant="additions"
>
  {#if conversation.length === 0}
    <EmptyState
      title="Welcome to Scholarly Explorer"
      description="Ask me about authors, venues, and publications in the knowledge graph."
    >
      {#snippet icon()}
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      {/snippet}
      <div class="examples">
        <p class="examples-title">Try asking:</p>
        <ul>
          <li>"Who are the most prolific authors?"</li>
          <li>"Which venues do they publish in?"</li>
          <li>"Show me publication trends over time"</li>
        </ul>
      </div>
    </EmptyState>
  {:else}
    {#each conversation as turn (turn.id)}
      {#if turn.role === 'user'}
        <UserMessage message={turn} />
      {:else}
        <AssistantMessage
          message={turn}
          result={results.get(turn.id) || null}
          observations={observations.get(turn.id) || []}
          suggestions={suggestions.get(turn.id) || []}
          filters={filtersByTurn.get(turn.id) || []}
          {onRemoveFilter}
          {onSelectSuggestion}
        />
      {/if}
    {/each}
  {/if}
</div>

<style>
  .conversation-container {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    background-color: var(--bg-secondary);
  }

  .examples {
    margin-top: 1.5rem;
    padding: 0.875rem;
    background-color: var(--bg-primary);
    border-radius: 6px;
    border: 1px solid var(--border);
    text-align: left;
    max-width: 320px;
  }

  .examples-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .examples ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .examples li {
    padding: 0.3125rem 0;
    font-size: 0.8125rem;
    color: var(--text-secondary);
  }

  @media (max-width: 640px) {
    .conversation-container {
      padding: 0.75rem;
    }

    .examples {
      max-width: 100%;
    }
  }
</style>
