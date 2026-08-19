<script lang="ts">
  import type { Filter } from '$lib/types/exploration';
  import { FACET_LABELS } from '$lib/types/exploration';

  let {
    filters,
    onRemove
  }: {
    filters: Filter[];
    onRemove: (index: number) => void;
  } = $props();
</script>

{#if filters.length > 0}
  <div class="active-filters">
    {#each filters as filter, index}
      <span class="filter-pill">
        <span class="filter-label">{FACET_LABELS[filter.field]} {filter.operator} {filter.value}</span>
        <button
          class="filter-remove"
          onclick={() => onRemove(index)}
          aria-label="Remove filter: {FACET_LABELS[filter.field]} {filter.operator} {filter.value}"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" x2="6" y1="6" y2="18"></line>
            <line x1="6" x2="18" y1="6" y2="18"></line>
          </svg>
        </button>
      </span>
    {/each}
  </div>
{/if}

<style>
  .active-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 0.375rem;
  }

  .filter-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.5rem;
    background-color: var(--filter-bg);
    color: var(--filter-text);
    border: 1px solid var(--filter-border);
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .filter-label {
    white-space: nowrap;
  }

  .filter-remove {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    padding: 0;
    background: transparent;
    border: none;
    border-radius: 50%;
    color: var(--filter-text);
    cursor: pointer;
    transition: background-color 0.15s ease, color 0.15s ease;
  }

  .filter-remove:hover {
    background-color: var(--error);
    color: white;
  }

  .filter-remove:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 1px;
  }
</style>
