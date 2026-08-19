<script lang="ts">
  import type { Facet, FacetRow, SortState } from '$lib/types/exploration';
  import { ALL_FACETS, FACET_LABELS } from '$lib/types/exploration';
  import FacetCell from './FacetCell.svelte';

  let {
    targetFacet,
    rows,
    sorting,
    loading = false,
    onCellClick,
    onCellHover,
    onCellHoverEnd
  }: {
    targetFacet: Facet | null;
    rows: FacetRow[];
    sorting: SortState | null;
    loading?: boolean;
    onCellClick: (rowIndex: number, facet: Facet) => void;
    onCellHover: (rowIndex: number, facet: Facet) => void;
    onCellHoverEnd: () => void;
  } = $props();

  let hoverPosition = $state({ x: 0, y: 0 });

  const displayFacets = ALL_FACETS.filter(f => f !== 'publication');

  function handleCellHover(event: MouseEvent, rowIndex: number, facet: Facet) {
    const rect = (event.target as HTMLElement).getBoundingClientRect();
    hoverPosition = { x: rect.left, y: rect.bottom + 4 };
    onCellHover(rowIndex, facet);
  }
</script>

<div class="facet-table-container">
  {#if loading}
    <div class="skeleton-table">
      {#each Array(5) as _, i}
        <div class="skeleton-row" style="animation-delay: {i * 0.1}s">
          <div class="skeleton-cell skeleton-target"></div>
          <div class="skeleton-cell"></div>
          <div class="skeleton-cell"></div>
          <div class="skeleton-cell"></div>
        </div>
      {/each}
    </div>
  {:else if !targetFacet && rows.length === 0}
    <div class="empty-state">
      <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"></circle>
        <path d="m21 21-4.3-4.3"></path>
      </svg>
      <p>Enter a question to begin exploring the scholarly literature.</p>
    </div>
  {:else}
    <div class="table-wrapper">
      <table class="facet-table">
        <thead>
          <tr>
            {#each displayFacets as facet (facet)}
              <th
                class:is-target={facet === targetFacet}
                scope="col"
              >
                <span class="th-content">
                  {FACET_LABELS[facet]}s
                  {#if sorting?.facet === facet}
                    <span class="sort-indicator">{sorting.direction === 'asc' ? '↑' : '↓'}</span>
                  {/if}
                </span>
              </th>
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each rows as row, rowIndex (row.targetValue)}
            <tr>
              {#each displayFacets as facet (facet)}
                {#if facet === targetFacet}
                  <FacetCell
                    value={row.targetValue}
                    isTarget={true}
                    {facet}
                  />
                {:else}
                  <FacetCell
                    value={row.connections[facet]}
                    isTarget={false}
                    {facet}
                    onActivate={() => onCellClick(rowIndex, facet)}
                    onHoverStart={() => onCellHover(rowIndex, facet)}
                    onHoverEnd={() => onCellHoverEnd()}
                  />
                {/if}
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    <p class="table-caption">
      {rows.length} {targetFacet ? FACET_LABELS[targetFacet].toLowerCase() + 's' : 'results'}
    </p>
  {/if}
</div>

<style>
  .facet-table-container {
    background-color: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
  }

  .table-wrapper {
    overflow-x: auto;
  }

  .facet-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8125rem;
  }

  th {
    padding: 0.625rem 0.75rem;
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    font-weight: 600;
    font-size: 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    white-space: nowrap;
  }

  th.is-target {
    background-color: var(--target-accent-light);
    border-left: 3px solid var(--target-accent);
    color: var(--accent);
  }

  .th-content {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
  }

  .sort-indicator {
    color: var(--accent);
    font-weight: 700;
  }

  .table-caption {
    padding: 0.5rem 0.75rem;
    font-size: 0.75rem;
    color: var(--text-muted);
    text-align: right;
    border-top: 1px solid var(--border-light);
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 1.5rem;
    text-align: center;
    color: var(--text-muted);
  }

  .empty-state svg {
    margin-bottom: 0.75rem;
    opacity: 0.5;
  }

  .empty-state p {
    font-size: 0.875rem;
    max-width: 280px;
  }

  .skeleton-table {
    padding: 0.5rem;
  }

  .skeleton-row {
    display: flex;
    gap: 0.5rem;
    padding: 0.5rem;
    animation: pulse 1.5s ease-in-out infinite;
  }

  .skeleton-cell {
    height: 1.5rem;
    flex: 1;
    background-color: var(--bg-tertiary);
    border-radius: 4px;
  }

  .skeleton-target {
    background-color: var(--target-accent-light);
  }
</style>
