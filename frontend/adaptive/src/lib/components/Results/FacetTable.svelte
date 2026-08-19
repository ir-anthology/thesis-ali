<script lang="ts">
  import type { ResultColumn, ResultRow, SortState } from '$lib/types/exploration';

  let {
    columns,
    rows,
    title,
    onSort
  }: {
    columns: ResultColumn[];
    rows: ResultRow[];
    title?: string;
    onSort?: (sort: SortState) => void;
  } = $props();

  let sortField = $state<string | null>(null);
  let sortDirection = $state<'asc' | 'desc'>('asc');

  function handleSort(column: ResultColumn): void {
    if (!column.sortable) return;
    if (sortField === column.key) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortField = column.key;
      sortDirection = 'asc';
    }
    onSort?.({ field: sortField, direction: sortDirection });
  }

  let sortedRows = $derived.by(() => {
    if (!sortField) return rows;
    return [...rows].sort((a, b) => {
      const aVal = a[sortField!];
      const bVal = b[sortField!];
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
      const cmp = String(aVal).localeCompare(String(bVal));
      return sortDirection === 'asc' ? cmp : -cmp;
    });
  });
</script>

<div class="table-container">
  {#if title}
    <div class="table-header">
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
        <line x1="3" x2="21" y1="9" y2="9"></line>
        <line x1="3" x2="21" y1="15" y2="15"></line>
        <line x1="9" x2="9" y1="3" y2="21"></line>
        <line x1="15" x2="15" y1="3" y2="21"></line>
      </svg>
      <span>{title}</span>
    </div>
  {/if}

  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          {#each columns as column}
            <th
              class:sortable={column.sortable}
              class:sorted={sortField === column.key}
              onclick={() => handleSort(column)}
            >
              <span class="th-content">
                {column.label}
                {#if sortField === column.key}
                  <span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                {/if}
              </span>
            </th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each sortedRows as row, i (i)}
          <tr>
            {#each columns as column}
              <td>
                {#if column.type === 'badge'}
                  <span class="cell-badge">{row[column.key]}</span>
                {:else}
                  {row[column.key]}
                {/if}
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>

<style>
  .table-container {
    margin-top: 0.625rem;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--code-border);
  }

  .table-header {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.625rem;
    background-color: var(--bg-secondary);
    border-bottom: 1px solid var(--code-border);
    font-size: 0.6875rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .table-wrapper {
    overflow-x: auto;
    background-color: var(--bg-primary);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8125rem;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  }

  th,
  td {
    padding: 0.5rem 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border-light);
    white-space: nowrap;
  }

  th {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    font-weight: 600;
    position: sticky;
    top: 0;
    font-size: 0.75rem;
  }

  th.sortable {
    cursor: pointer;
    user-select: none;
  }

  th.sortable:hover {
    background-color: var(--bg-tertiary);
  }

  th.sorted {
    color: var(--accent);
  }

  .th-content {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
  }

  .sort-indicator {
    font-size: 0.625rem;
  }

  td {
    color: var(--text-primary);
  }

  tr:last-child td {
    border-bottom: none;
  }

  tbody tr:hover td {
    background-color: var(--bg-secondary);
  }

  tbody tr {
    transition: background-color 0.1s ease;
  }

  .cell-badge {
    display: inline-block;
    padding: 0.0625rem 0.375rem;
    font-size: 0.6875rem;
    font-weight: 500;
    background-color: var(--bg-tertiary);
    border-radius: 9999px;
    color: var(--text-secondary);
  }
</style>
