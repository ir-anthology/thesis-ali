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
        {showSparql ? 'Result' : 'Sparql'}
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
    padding: 0.125rem 0.5rem;
    font-size: 0.6875rem;
    font-weight: 500;
    font-family: inherit;
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--text-secondary);
    cursor: pointer;
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
