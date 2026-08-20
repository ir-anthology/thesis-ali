<script lang="ts">
  import type { ResultState } from '$lib/types/exploration';
  import ExplorationRenderer from './ExplorationRenderer.svelte';
  import SparqlBlock from './SparqlBlock.svelte';

  let {
    result,
    sparqlQuery
  }: {
    result: ResultState;
    sparqlQuery?: string;
  } = $props();

  let activeTab = $state<'result' | 'sparql'>('result');
</script>

<div class="result-box">
  {#if sparqlQuery}
    <div class="result-tabs" role="tablist" aria-label="Result view">
      <button
        class="tab-btn"
        class:active={activeTab === 'result'}
        onclick={() => activeTab = 'result'}
        role="tab"
        aria-selected={activeTab === 'result'}
        aria-controls="result-panel"
      >
        Result View
      </button>
      <button
        class="tab-btn"
        class:active={activeTab === 'sparql'}
        onclick={() => activeTab = 'sparql'}
        role="tab"
        aria-selected={activeTab === 'sparql'}
        aria-controls="sparql-panel"
      >
        SPARQL Query
      </button>
    </div>
  {/if}

  {#if activeTab === 'result' || !sparqlQuery}
    <div id="result-panel" role="tabpanel">
      <ExplorationRenderer {result} />
    </div>
  {:else}
    <div id="sparql-panel" role="tabpanel">
      <SparqlBlock query={sparqlQuery} />
    </div>
  {/if}
</div>

<style>
  .result-box {
    margin-top: 0.625rem;
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
  }

  .result-tabs {
    display: flex;
    border-bottom: 1px solid var(--border);
    background-color: var(--bg-secondary);
  }

  .tab-btn {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 500;
    font-family: inherit;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-secondary);
    cursor: pointer;
    transition: color 0.15s ease, border-color 0.15s ease, background-color 0.15s ease;
  }

  .tab-btn:hover {
    color: var(--text-primary);
    background-color: var(--bg-tertiary);
  }

  .tab-btn.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
    background-color: var(--bg-primary);
  }

  .tab-btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: -2px;
  }
</style>
