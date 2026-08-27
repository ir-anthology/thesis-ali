<script lang="ts">
  import type { ResultColumn, ResultRow } from '$lib/types/exploration';
  import FacetTable from './FacetTable.svelte';
  import SparqlBlock from './SparqlBlock.svelte';

  let {
    columns,
    rows,
    sparqlQuery
  }: {
    columns: ResultColumn[];
    rows: ResultRow[];
    sparqlQuery?: string;
  } = $props();

  let showSparql = $state(true);
</script>

<div class="result-box">
  {#if sparqlQuery}
    <div class="result-tabs" role="tablist" aria-label="Result view">
      <button
        class="tab-btn"
        class:active={showSparql}
        onclick={() => showSparql = true}
        role="tab"
        aria-selected={showSparql}
      >
        Sparql Query
      </button>
      <button
        class="tab-btn"
        class:active={!showSparql}
        onclick={() => showSparql = false}
        role="tab"
        aria-selected={!showSparql}
      >
        Result Table
      </button>
    </div>
  {/if}

  {#if showSparql && sparqlQuery}
    <div role="tabpanel">
      <SparqlBlock query={sparqlQuery} />
    </div>
  {:else}
    <div role="tabpanel">
      <FacetTable {columns} {rows} />
    </div>
  {/if}
</div>

<style>
  .result-box {
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
