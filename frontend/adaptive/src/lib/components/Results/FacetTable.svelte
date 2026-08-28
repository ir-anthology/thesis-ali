<script lang="ts">
  import type { ResultColumn, ResultRow } from '$lib/types/exploration';

  let {
    columns,
    rows,
    title,
    onCellClick
  }: {
    columns: ResultColumn[];
    rows: ResultRow[];
    title?: string;
    onCellClick?: (question: string) => void;
  } = $props();

  let sortField = $state<string | null>(null);
  let sortDirection = $state<'asc' | 'desc'>('asc');
  let focusedRowIndex = $state(-1);
  let tableElement: HTMLTableElement | undefined = $state();

  function handleSort(column: ResultColumn): void {
    if (!column.sortable) return;
    if (sortField === column.key) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortField = column.key;
      sortDirection = 'asc';
    }
  }

  function handleKeydown(event: KeyboardEvent, rowIndex: number): void {
    const rows = tableElement?.querySelectorAll('tbody tr');
    if (!rows) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        if (rowIndex < rows.length - 1) {
          focusedRowIndex = rowIndex + 1;
          (rows[focusedRowIndex] as HTMLElement).focus();
        }
        break;
      case 'ArrowUp':
        event.preventDefault();
        if (rowIndex > 0) {
          focusedRowIndex = rowIndex - 1;
          (rows[focusedRowIndex] as HTMLElement).focus();
        }
        break;
      case 'Home':
        event.preventDefault();
        focusedRowIndex = 0;
        (rows[0] as HTMLElement).focus();
        break;
      case 'End':
        event.preventDefault();
        focusedRowIndex = rows.length - 1;
        (rows[rows.length - 1] as HTMLElement).focus();
        break;
      case 'Escape':
        event.preventDefault();
        focusedRowIndex = -1;
        (event.target as HTMLElement).blur();
        break;
    }
  }

  let sortedRows = $derived.by(() => {
    if (!sortField) return rows;
    return [...rows].sort((a, b) => {
      const aVal = a[sortField!].value;
      const bVal = b[sortField!].value;
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
      const cmp = String(aVal).localeCompare(String(bVal));
      return sortDirection === 'asc' ? cmp : -cmp;
    });
  });
</script>

<div class="table-container">
  <div class="table-wrapper">
    <table bind:this={tableElement} role="grid" aria-label={title || 'Data table'}>
      <thead>
        <tr>
          {#each columns as column}
            <th
              role="columnheader"
              class:sortable={column.sortable}
              class:sorted={sortField === column.key}
              onclick={() => handleSort(column)}
              aria-sort={sortField === column.key ? (sortDirection === 'asc' ? 'ascending' : 'descending') : 'none'}
            >
              <span class="th-content">
                {column.label}
                {#if sortField === column.key}
                  <span class="sort-indicator" aria-hidden="true">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                {/if}
              </span>
            </th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each sortedRows as row, i (i)}
          <tr
            tabindex={focusedRowIndex === i ? 0 : -1}
            onkeydown={(e) => handleKeydown(e, i)}
            onfocus={() => focusedRowIndex = i}
            class:focused={focusedRowIndex === i}
          >
            {#each columns as column}
              {@const cell = row[column.key]}
              <td
                role="gridcell"
                class:clickable={!!onCellClick && !!cell.question}
                title={cell.question || undefined}
                onclick={cell.question ? () => onCellClick?.(cell.question) : undefined}
              >
                {#if column.type === 'badge'}
                  <span class="cell-badge">{cell.value}</span>
                {:else}
                  {cell.value}
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
    border-radius: 0;
    overflow: hidden;
    border: none;
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
    text-align: center;
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

  td.clickable {
    cursor: pointer;
    transition: background-color 0.1s ease;
  }

  td.clickable:hover {
    background-color: var(--accent-light);
    color: var(--accent);
  }

  tr:last-child td {
    border-bottom: none;
  }

  tbody tr:hover td {
    background-color: var(--bg-secondary);
  }

  tbody tr.focused td {
    background-color: var(--accent-light);
    outline: 2px solid var(--accent);
    outline-offset: -2px;
  }

  tbody tr {
    transition: background-color 0.1s ease;
    outline: none;
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
