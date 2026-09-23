<script lang="ts">
  import { tick } from 'svelte';
  import type { CellQuestionContext, ConversationTurn, EntityInteraction, ResultColumn, ResultRow, StatisticsResponse } from '$lib/types/exploration';
  import UserMessage from './UserMessage.svelte';
  import AssistantMessage from './AssistantMessage.svelte';
  import EmptyState from '$lib/components/Shared/EmptyState.svelte';
  import FacetTable from '$lib/components/Results/FacetTable.svelte';
  import { analyticsHeaders } from '$lib/analytics';

  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

  let {
    conversation,
    interpretationByTurn,
    columnsByTurn,
    rowsByTurn,
    observationsByTurn,
    suggestionsByTurn,
    sparqlByTurn,
    disabled = false,
    onSelectSuggestion,
    onCellQuestion,
    onEditUserPrompt,
    activePath
  }: {
    conversation: ConversationTurn[];
    interpretationByTurn: Map<string, string>;
    columnsByTurn: Map<string, ResultColumn[]>;
    rowsByTurn: Map<string, ResultRow[]>;
    observationsByTurn: Map<string, string[]>;
    suggestionsByTurn: Map<string, string[]>;
    sparqlByTurn: Map<string, string>;
    disabled?: boolean;
    onSelectSuggestion: (suggestion: string, fromTurnId?: string | null, interaction?: EntityInteraction) => void;
    onCellQuestion: (
      context: CellQuestionContext,
      fromTurnId: string,
      interaction?: EntityInteraction
    ) => void;
    onEditUserPrompt?: (turnId: string, content: string) => void;
    activePath: ConversationTurn[];
  } = $props();

  let statistics = $state<StatisticsResponse | null>(null);
  let statsLoading = $state(true);
  let statsError = $state<string | null>(null);

  async function fetchStatistics(): Promise<void> {
    try {
      statsLoading = true;
      statsError = null;
      const res = await fetch(`${API_BASE}/api/statistics`, {
        headers: analyticsHeaders()
      });
      if (!res.ok) {
        throw new Error(`Failed to fetch statistics: ${res.status}`);
      }
      statistics = await res.json();
    } catch (e) {
      statsError = e instanceof Error ? e.message : 'Failed to load statistics';
    } finally {
      statsLoading = false;
    }
  }

  $effect(() => {
    fetchStatistics();
  });

  function handleOverviewClick(
    _context: CellQuestionContext,
    interaction?: EntityInteraction,
    existingQuestion?: string
  ): void {
    if (disabled) return;
    if (existingQuestion) onSelectSuggestion(existingQuestion, null, interaction);
  }

  $effect(() => {
    const turnCount = activePath.length;
    if (turnCount > 0) {
      tick().then(() => {
        window.scrollTo({
          top: document.documentElement.scrollHeight,
          behavior: 'smooth'
        });
      });
    }
  });
</script>

<div
  class="conversation-container"
  class:has-conversation={conversation.length > 0}
  role="log"
  aria-label="Conversation history"
  aria-live="polite"
  aria-relevant="additions"
>
  <div class="conversation-content">
    <div class="welcome-section" class:centered={conversation.length === 0} class:compact={conversation.length > 0}>
      <EmptyState
        title="Welcome to IR Anthology Chat"
        description="Ask me about authors, venues, and publications in the knowledge graph."
      >
        {#if conversation.length === 0}
          {#snippet icon()}
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          {/snippet}
        {/if}
      </EmptyState>
      {#if statsLoading}
        <div class="stats-loading">
          <div class="spinner"></div>
          <span>Loading statistics...</span>
        </div>
      {:else if statsError}
        <div class="stats-error">
          <span>{statsError}</span>
        </div>
      {:else if statistics}
        <div class="overview-wrapper" id="stats-table" data-meta="stats-table">
          <FacetTable
            columns={statistics.columns}
            rows={statistics.rows}
            title="Knowledge Graph Overview"
            onCellClick={handleOverviewClick}
            tableId="stats-facet-table"
            dataMeta="statistics"
            disabled={disabled}
          />
        </div>
      {/if}
    </div>

    {#each activePath as turn (turn.id)}
      {#if turn.role === 'user'}
        <UserMessage message={turn} {disabled} onEdit={onEditUserPrompt} />
      {:else}
        <AssistantMessage
          message={turn}
          interpretation={interpretationByTurn.get(turn.id)}
          columns={columnsByTurn.get(turn.id)}
          rows={rowsByTurn.get(turn.id)}
          observations={observationsByTurn.get(turn.id)}
          suggestions={suggestionsByTurn.get(turn.id)}
          sparqlQuery={sparqlByTurn.get(turn.id)}
          disabled={disabled}
          onSelectSuggestion={(s) => onSelectSuggestion(s, turn.id)}
          onCellClick={(context, interaction, existingQuestion) => {
            if (existingQuestion) {
              onSelectSuggestion(existingQuestion, turn.id, interaction);
            } else {
              onCellQuestion(context, turn.id, interaction);
            }
          }}
        />
      {/if}
    {/each}
  </div>
</div>

<style>
  .conversation-container {
    flex: 1;
    padding: 1rem;
    background-color: var(--bg-secondary);
    display: flex;
    flex-direction: column;
    transition: padding 0.3s ease;
  }

  .conversation-content {
    width: 100%;
    max-width: none;
  }

  .conversation-container.has-conversation {
    padding-top: 1rem;
  }

  .welcome-section {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 1.25rem;
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
    width: 100%;
  }

  .welcome-section.centered {
    flex: 1;
    align-items: center;
    justify-content: center;
    margin-bottom: 0;
  }

  .welcome-section :global(.empty-state) {
    height: auto;
    transition: all 0.3s ease;
  }

  .welcome-section.compact {
    align-items: flex-start;
    gap: 0.5rem;
  }

  .welcome-section.compact :global(.empty-state) {
    text-align: left;
    align-items: flex-start;
    padding: 0;
    margin-bottom: 0;
  }

  .welcome-section.compact :global(.empty-icon) {
    display: none;
  }

  .welcome-section.compact :global(.empty-actions) {
    display: none;
  }

  .welcome-section.compact :global(.empty-description) {
    margin-bottom: 0;
    max-width: none;
    width: fit-content;
  }

  .welcome-section.compact :global(.empty-title) {
    width: fit-content;
  }

  .overview-wrapper {
    max-width: 480px;
    width: 100%;
    background-color: var(--bg-primary);
    border-radius: 6px;
    border: 1px solid var(--border);
    overflow: hidden;
    transition: all 0.3s ease;
  }

  .stats-loading {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-secondary);
    font-size: 0.875rem;
  }

  .stats-error {
    color: var(--error);
    font-size: 0.875rem;
    padding: 0.75rem;
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 6px;
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
