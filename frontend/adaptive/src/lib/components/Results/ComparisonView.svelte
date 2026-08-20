<script lang="ts">
  import type { ResultColumn, ResultRow } from '$lib/types/exploration';

  let {
    columns,
    rows,
    title
  }: {
    columns: ResultColumn[];
    rows: ResultRow[];
    title?: string;
  } = $props();
</script>

<div class="comparison-container">
  <div class="comparison-table-wrapper">
    <table>
      <thead>
        <tr>
          {#each columns as column}
            <th>{column.label}</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each rows as row, i (i)}
          <tr>
            {#each columns as column, j}
              <td class:metric-cell={j === 0}>{row[column.key]}</td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>

<style>
  .comparison-container {
    margin-top: 0.625rem;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--code-border);
  }

  .comparison-table-wrapper {
    overflow-x: auto;
    background-color: var(--bg-primary);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8125rem;
  }

  th,
  td {
    padding: 0.5rem 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border-light);
  }

  th {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    font-weight: 600;
    font-size: 0.75rem;
  }

  .metric-cell {
    font-weight: 500;
    color: var(--text-secondary);
    font-size: 0.75rem;
  }

  tr:last-child td {
    border-bottom: none;
  }

  tbody tr:hover td {
    background-color: var(--bg-secondary);
  }
</style>
