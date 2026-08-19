<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import SearchPanel from '$lib/components/SearchPanel.svelte';
  import FacetToolbar from '$lib/components/FacetToolbar.svelte';
  import FacetTable from '$lib/components/FacetTable.svelte';
  import InsightsPanel from '$lib/components/InsightsPanel.svelte';
  import LoadingState from '$lib/components/LoadingState.svelte';
  import UnsupportedState from '$lib/components/UnsupportedState.svelte';
  import ErrorState from '$lib/components/ErrorState.svelte';
  import PromptTooltip from '$lib/components/PromptTooltip.svelte';
  import { explorationStore } from '$lib/stores/exploration.svelte';
</script>

<svelte:head>
  <title>Scholarly Explorer</title>
  <meta name="description" content="LLM-Assisted Exploratory Search in Scholarly Knowledge Graphs" />
</svelte:head>

<div class="app">
  <Header
    promptOutputMode={explorationStore.promptOutputMode}
    onToggleMode={() => explorationStore.togglePromptMode()}
  />

  <main class="main-content">
    <SearchPanel
      value={explorationStore.input}
      disabled={explorationStore.loadingStage !== null}
      generatedPrompt={explorationStore.generatedPrompt?.text ?? null}
      onSubmit={(text) => explorationStore.submitQuestion(text)}
      onInput={(text) => { explorationStore.input = text; }}
    />

    {#if explorationStore.loadingStage}
      <LoadingState stage={explorationStore.loadingStage} />
    {/if}

    {#if explorationStore.error}
      {#if explorationStore.error.type === 'unsupported'}
        <UnsupportedState
          suggestions={explorationStore.error.suggestions ?? []}
          onSuggestionClick={(text) => explorationStore.selectFollowUp(text)}
        />
      {:else}
        <ErrorState
          error={explorationStore.error}
          onRetry={() => explorationStore.submitQuestion(explorationStore.input)}
        />
      {/if}
    {/if}

    {#if explorationStore.hasSubmitted && !explorationStore.loadingStage && !explorationStore.error}
      <div class="workspace">
        <div class="workspace-left">
          <FacetToolbar
            targetFacet={explorationStore.targetFacet}
            filters={explorationStore.filters}
            sortState={explorationStore.sorting}
            onRemoveFilter={(i) => explorationStore.removeFilter(i)}
            onSort={(facet) => explorationStore.sortFacet(facet)}
          />
          <FacetTable
            targetFacet={explorationStore.targetFacet}
            rows={explorationStore.rows}
            sorting={explorationStore.sorting}
            loading={false}
            onCellClick={(rowIdx, facet) => explorationStore.pivotCell(rowIdx, facet)}
            onCellHover={() => {}}
            onCellHoverEnd={() => explorationStore.clearPrompt()}
          />
        </div>
        <div class="workspace-right">
          <InsightsPanel
            observations={explorationStore.observations}
            followUpQuestions={explorationStore.followUpQuestions}
            onFollowUp={(text) => explorationStore.selectFollowUp(text)}
          />
        </div>
      </div>
    {/if}

    {#if !explorationStore.hasSubmitted && !explorationStore.loadingStage}
      <div class="welcome">
        <div class="welcome-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"></path>
            <path d="M2 12h20"></path>
          </svg>
        </div>
        <h2>Welcome to Scholarly Explorer</h2>
        <p>Ask a question about the scholarly literature to begin exploring.</p>
        <div class="examples">
          <p class="example-title">Try asking:</p>
          <ul>
            <li
              role="button"
              tabindex="0"
              onclick={() => explorationStore.submitQuestion('Who are the most prolific authors?')}
              onkeydown={(e) => { if (e.key === 'Enter') explorationStore.submitQuestion('Who are the most prolific authors?'); }}
            >
              "Who are the most prolific authors?"
            </li>
            <li
              role="button"
              tabindex="0"
              onclick={() => explorationStore.submitQuestion('Which venues have the most publications?')}
              onkeydown={(e) => { if (e.key === 'Enter') explorationStore.submitQuestion('Which venues have the most publications?'); }}
            >
              "Which venues have the most publications?"
            </li>
            <li
              role="button"
              tabindex="0"
              onclick={() => explorationStore.submitQuestion('How has publication output changed over time?')}
              onkeydown={(e) => { if (e.key === 'Enter') explorationStore.submitQuestion('How has publication output changed over time?'); }}
            >
              "How has publication output changed over time?"
            </li>
          </ul>
        </div>
      </div>
    {/if}
  </main>

  {#if explorationStore.promptOutputMode === 'tooltip' && explorationStore.generatedPrompt}
    <PromptTooltip
      text={explorationStore.generatedPrompt.text}
      visible={true}
      position={explorationStore.tooltipPosition}
    />
  {/if}
</div>

<style>
  .app {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
  }

  .main-content {
    flex: 1;
    overflow-y: auto;
    background-color: var(--bg-secondary);
  }

  .workspace {
    display: grid;
    grid-template-columns: 1fr 360px;
    gap: 1rem;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem 1rem;
    min-height: 0;
  }

  .workspace-left {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    min-width: 0;
  }

  .workspace-right {
    min-height: 0;
  }

  .welcome {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    padding: 1.5rem;
  }

  .welcome-icon {
    color: var(--accent);
    margin-bottom: 0.75rem;
    opacity: 0.8;
  }

  .welcome h2 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.375rem;
    letter-spacing: -0.01em;
  }

  .welcome p {
    color: var(--text-secondary);
    max-width: 320px;
    font-size: 0.875rem;
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

  .example-title {
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
    cursor: pointer;
    transition: color 0.15s ease;
  }

  .examples li:hover {
    color: var(--accent);
  }

  .examples li:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
    border-radius: 2px;
  }

  @media (max-width: 1024px) {
    .workspace {
      grid-template-columns: 1fr 300px;
    }
  }

  @media (max-width: 768px) {
    .workspace {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 640px) {
    .welcome {
      padding: 1rem;
    }

    .welcome h2 {
      font-size: 1rem;
    }

    .examples {
      max-width: 100%;
    }
  }
</style>
