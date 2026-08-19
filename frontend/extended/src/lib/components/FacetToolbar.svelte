<script lang="ts">
  import type { Facet, Filter, SortState } from '$lib/types/exploration';
  import { FACET_LABELS } from '$lib/types/exploration';
  import ActiveFilters from './ActiveFilters.svelte';

  let {
    targetFacet,
    filters,
    sortState,
    onRemoveFilter,
    onSort
  }: {
    targetFacet: Facet | null;
    filters: Filter[];
    sortState: SortState | null;
    onRemoveFilter: (index: number) => void;
    onSort: (facet: Facet) => void;
  } = $props();

  function getSortLabel(): string {
    if (!sortState) return 'Sort';
    return `${FACET_LABELS[sortState.facet]} ${sortState.direction === 'asc' ? '↑' : '↓'}`;
  }
</script>

<div class="facet-toolbar">
  <div class="toolbar-left">
    {#if targetFacet}
      <span class="target-badge">
        <span class="target-label">Target</span>
        <span class="target-value">{FACET_LABELS[targetFacet]}s</span>
      </span>
    {/if}
    <ActiveFilters {filters} onRemove={onRemoveFilter} />
  </div>

  <div class="toolbar-right">
    {#each ['author', 'venue', 'year', 'publication'] as facet (facet)}
      <button
        class="sort-btn"
        class:active={sortState?.facet === facet}
        onclick={() => onSort(facet as Facet)}
        aria-label="Sort by {FACET_LABELS[facet as Facet]}"
      >
        {FACET_LABELS[facet as Facet]}
        {#if sortState?.facet === facet}
          {sortState.direction === 'asc' ? '↑' : '↓'}
        {/if}
      </button>
    {/each}
  </div>
</div>

<style>
  .facet-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.75rem 1rem;
    background-color: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 0.5rem;
    flex-wrap: wrap;
  }

  .toolbar-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
    min-width: 0;
  }

  .target-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.625rem;
    background-color: var(--accent);
    color: white;
    border-radius: 9999px;
    font-size: 0.75rem;
    white-space: nowrap;
    flex-shrink: 0;
  }

  .target-label {
    font-weight: 400;
    opacity: 0.8;
  }

  .target-value {
    font-weight: 600;
  }

  .toolbar-right {
    display: flex;
    gap: 0.25rem;
    flex-shrink: 0;
  }

  .sort-btn {
    padding: 0.25rem 0.5rem;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    font-size: 0.75rem;
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
  }

  .sort-btn:hover {
    color: var(--text-secondary);
    border-color: var(--border);
  }

  .sort-btn.active {
    color: var(--accent);
    background-color: var(--accent-light);
    border-color: var(--accent);
  }

  .sort-btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }

  @media (max-width: 768px) {
    .facet-toolbar {
      flex-direction: column;
      align-items: flex-start;
    }

    .toolbar-right {
      width: 100%;
      overflow-x: auto;
    }
  }
</style>
