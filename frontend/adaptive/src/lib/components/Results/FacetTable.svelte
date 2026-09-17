<script lang="ts">
  import type { CellMetadata, EntityInteraction, ResultColumn, ResultRow } from '$lib/types/exploration';

  let {
    columns,
    rows,
    title,
    onCellClick,
    tableId,
    dataMeta,
    fitContent = false
  }: {
    columns: ResultColumn[];
    rows: ResultRow[];
    title?: string;
    onCellClick?: (question: string, interaction?: EntityInteraction) => void;
    tableId?: string;
    dataMeta?: string;
    fitContent?: boolean;
  } = $props();

  const HTTP_URL_RE = /^https?:\/\/[^\s]+$/i;

  let visibleColumns = $derived(
    columns.filter((column) => column.visible && !column.external_link)
  );

  function getExternalLinks(
    row: ResultRow,
    relatedColumnKey: string
  ): Array<{ key: string; label: string; href: string }> {
    return columns
      .filter(
        (column) =>
          column.external_link && column.related_column === relatedColumnKey
      )
      .flatMap((column) => {
        const value = row[column.key]?.value;
        if (typeof value !== 'string' || !HTTP_URL_RE.test(value)) return [];
        return [{ key: column.key, label: column.label, href: value }];
      });
  }

  function getEntityMetadata(row: ResultRow, cellKey: string): CellMetadata | undefined {
    const direct = row[cellKey]?.metadata;
    if (direct?.entity_id) return direct;

    const candidates = [`${cellKey}_id`, `${cellKey}_uri`];
    if (cellKey.endsWith('_name')) {
      const prefix = cellKey.slice(0, -'_name'.length);
      candidates.push(`${prefix}_id`, `${prefix}_uri`);
    }
    if (cellKey === 'title' || cellKey === 'name') {
      candidates.push('pub_id', 'publication_id', 'pub_uri', 'publication_uri');
    }
    for (const key of candidates) {
      const metadata = row[key]?.metadata;
      if (metadata?.entity_id) return metadata;
    }

    const metadataColumns = columns.filter((column) => !column.visible);
    if (metadataColumns.length !== 1) return undefined;
    for (const column of columns) {
      if (column.visible) continue;
      const metadata = row[column.key]?.metadata;
      if (metadata?.entity_id) return metadata;
    }
    return undefined;
  }

  let sortField = $state<string | null>(null);
  let sortDirection = $state<'asc' | 'desc'>('asc');
  let focusedRowIndex = $state(-1);
  let focusedCellKey = $state<string | null>(null);
  let focusedCellRow = $state(-1);
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

  function handleCellClick(question: string, columnKey: string, row: ResultRow, rowIndex: number): void {
    focusedCellKey = columnKey;
    focusedCellRow = rowIndex;
    const metadata = getEntityMetadata(row, columnKey);
    const interaction = metadata?.entity_id
      ? { entity_id: metadata.entity_id, entity_type: metadata.entity_type }
      : undefined;
    onCellClick?.(question, interaction);
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

  function toNumericValue(value: string | number): number | null {
    if (typeof value === 'number') {
      return Number.isFinite(value) ? value : null;
    }

    if (!value.trim()) return null;

    const numericValue = Number(value);
    return Number.isFinite(numericValue) ? numericValue : null;
  }

  function compareValues(a: string | number, b: string | number): number {
    const aNumber = toNumericValue(a);
    const bNumber = toNumericValue(b);

    if (aNumber !== null && bNumber !== null) {
      return aNumber - bNumber;
    }

    return String(a).localeCompare(String(b));
  }

  let sortedRows = $derived.by(() => {
    if (!sortField) return rows;
    if (!visibleColumns.some((column) => column.key === sortField)) return rows;
    return [...rows].sort((a, b) => {
      const aVal = a[sortField!].value;
      const bVal = b[sortField!].value;
      const cmp = compareValues(aVal, bVal);
      return sortDirection === 'asc' ? cmp : -cmp;
    });
  });
</script>

<div class="table-container" class:fit-content-table={fitContent} id={tableId} data-meta={dataMeta}>
  <div class="table-wrapper">
    <table bind:this={tableElement} role="grid" aria-label={title || 'Data table'}>
      <thead>
        <tr>
          {#each visibleColumns as column}
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
            {#each visibleColumns as column, j (j)}
              {@const cell = row[column.key]}
              {@const externalLinks = getExternalLinks(row, column.key)}
              <td
                role="gridcell"
                class:clickable={!!onCellClick && !!cell.question}
                class:focused={focusedCellKey === column.key && focusedCellRow === i}
                title={cell.question || undefined}
                data-entity-id={getEntityMetadata(row, column.key)?.entity_id}
                data-entity-type={getEntityMetadata(row, column.key)?.entity_type}
                onclick={cell.question ? () => handleCellClick(cell.question, column.key, row, i) : undefined}
              >
                {#if column.type === 'badge'}
                  <span class="cell-badge">{cell.value}</span>
                {:else}
                  {cell.value}
                {/if}
                {#each externalLinks as externalLink (externalLink.key)}
                  <a
                    class="external-link"
                    href={externalLink.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={`Open ${externalLink.label}`}
                    title={`Open ${externalLink.label}`}
                    onclick={(event) => event.stopPropagation()}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="13"
                      height="13"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      aria-hidden="true"
                    >
                      <path d="M15 3h6v6"></path>
                      <path d="M10 14 21 3"></path>
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    </svg>
                  </a>
                {/each}
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
    max-width: 100%;
    overflow-x: auto;
    background-color: var(--bg-primary);
  }

  .fit-content-table .table-wrapper {
    width: fit-content;
  }

  .fit-content-table table {
    width: max-content;
    min-width: 0;
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

  tbody tr {
    transition: background-color 0.1s ease;
    outline: none;
  }

  td.focused {
    background-color: var(--accent-light);
    outline: 2px solid var(--accent);
    outline-offset: -2px;
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

  .external-link {
    display: inline-flex;
    align-items: center;
    margin-left: 0.375rem;
    color: var(--accent);
    vertical-align: -0.1em;
  }

  .external-link:hover {
    color: var(--accent-hover);
  }

  .external-link:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
    border-radius: 2px;
  }
</style>
