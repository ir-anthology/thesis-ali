<script lang="ts">
  import type { ConversationTurn, ResultColumn, ResultRow } from '$lib/types/exploration';
  import UserMessage from './UserMessage.svelte';
  import AssistantMessage from './AssistantMessage.svelte';
  import EmptyState from '$lib/components/Shared/EmptyState.svelte';
  import FacetTable from '$lib/components/Results/FacetTable.svelte';
  import { overviewData } from '$lib/data/mock-overview';

  let {
    conversation,
    intentByTurn,
    clarificationByTurn,
    limitationByTurn,
    columnsByTurn,
    rowsByTurn,
    observationsByTurn,
    suggestionsByTurn,
    sparqlByTurn,
    onSelectSuggestion
  }: {
    conversation: ConversationTurn[];
    intentByTurn: Map<string, string>;
    clarificationByTurn: Map<string, string>;
    limitationByTurn: Map<string, string>;
    columnsByTurn: Map<string, ResultColumn[]>;
    rowsByTurn: Map<string, ResultRow[]>;
    observationsByTurn: Map<string, string[]>;
    suggestionsByTurn: Map<string, string[]>;
    sparqlByTurn: Map<string, string>;
    onSelectSuggestion: (suggestion: string) => void;
  } = $props();

  let container: HTMLDivElement | undefined = $state();

  function handleOverviewClick(question: string): void {
    onSelectSuggestion(question);
  }

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
    <div class="empty-container">
      <EmptyState
        title="Welcome to IR Anthology Chat"
        description="Ask me about authors, venues, and publications in the knowledge graph."
      >
        {#snippet icon()}
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        {/snippet}
      </EmptyState>
      <div class="overview-wrapper">
        <FacetTable
          columns={overviewData.columns}
          rows={overviewData.rows}
          title={overviewData.title}
          onCellClick={handleOverviewClick}
        />
      </div>
    </div>
  {:else}
    {#each conversation as turn (turn.id)}
      {#if turn.role === 'user'}
        <UserMessage message={turn} />
      {:else}
        <AssistantMessage
          message={turn}
          intent={intentByTurn.get(turn.id)}
          clarification={clarificationByTurn.get(turn.id)}
          limitation={limitationByTurn.get(turn.id)}
          columns={columnsByTurn.get(turn.id)}
          rows={rowsByTurn.get(turn.id)}
          observations={observationsByTurn.get(turn.id)}
          suggestions={suggestionsByTurn.get(turn.id)}
          sparqlQuery={sparqlByTurn.get(turn.id)}
          {onSelectSuggestion}
          onCellClick={onSelectSuggestion}
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

  .empty-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 1.25rem;
  }

  .empty-container :global(.empty-state) {
    height: auto;
  }

  .overview-wrapper {
    max-width: 480px;
    width: 100%;
    background-color: var(--bg-primary);
    border-radius: 6px;
    border: 1px solid var(--border);
    overflow: hidden;
  }

  @media (max-width: 640px) {
    .conversation-container {
      padding: 0.75rem;
    }

    .overview-wrapper {
      max-width: 100%;
    }
  }
</style>
