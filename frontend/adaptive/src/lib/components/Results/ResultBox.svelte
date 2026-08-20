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

  let showSparql = $state(true);

  function toggle(): void {
    showSparql = !showSparql;
  }
</script>

<div class="result-box">
  {#if sparqlQuery}
    <div class="result-header">
      <button
        class="toggle-btn"
        onclick={toggle}
        title={showSparql ? 'Show Result View' : 'Show SPARQL Query'}
        aria-label={showSparql ? 'Show Result View' : 'Show SPARQL Query'}
      >
        {#if showSparql}
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
            <line x1="3" x2="21" y1="9" y2="9"></line>
            <line x1="3" x2="21" y1="15" y2="15"></line>
            <line x1="9" x2="9" y1="3" y2="21"></line>
          </svg>
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="16 18 22 12 16 6"></polyline>
            <polyline points="8 6 2 12 8 18"></polyline>
          </svg>
        {/if}
      </button>
    </div>
  {/if}

  {#if showSparql && sparqlQuery}
    <div role="tabpanel">
      <SparqlBlock query={sparqlQuery} />
    </div>
  {:else}
    <div role="tabpanel">
      <ExplorationRenderer {result} />
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

  .result-header {
    display: flex;
    justify-content: flex-end;
    padding: 0.25rem 0.5rem;
    border-bottom: 1px solid var(--border);
    background-color: var(--bg-secondary);
  }

  .toggle-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 0;
    transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
  }

  .toggle-btn:hover {
    background-color: var(--accent-light);
    color: var(--accent);
    border-color: var(--accent);
  }

  .toggle-btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
</style>
