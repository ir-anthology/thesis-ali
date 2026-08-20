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

  let labelColumn = $derived(columns[0]);
  let dataColumns = $derived(columns.slice(1));

  let maxValue = $derived.by(() => {
    let max = 0;
    for (const row of rows) {
      for (const col of dataColumns) {
        const val = Number(row[col.key]) || 0;
        if (val > max) max = val;
      }
    }
    return max;
  });
</script>

<div class="timeline-container">
  <div class="timeline-body">
    {#each rows as row, i (i)}
      <div class="timeline-row">
        <span class="timeline-label">{row[labelColumn.key]}</span>
        <div class="timeline-bars">
          {#each dataColumns as col}
            <div class="bar-group">
              <div
                class="bar"
                style="width: {((Number(row[col.key]) || 0) / maxValue) * 100}%"
              ></div>
              <span class="bar-value">{row[col.key]}</span>
            </div>
          {/each}
        </div>
      </div>
    {/each}
  </div>

  {#if dataColumns.length > 1}
    <div class="timeline-legend">
      {#each dataColumns as col}
        <span class="legend-item">
          <span class="legend-dot"></span>
          {col.label}
        </span>
      {/each}
    </div>
  {/if}
</div>

<style>
  .timeline-container {
    border-radius: 0;
    overflow: hidden;
    border: none;
    background-color: var(--bg-primary);
  }

  .timeline-body {
    padding: 0.75rem;
  }

  .timeline-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }

  .timeline-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-secondary);
    min-width: 2.5rem;
    text-align: right;
  }

  .timeline-bars {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.125rem;
  }

  .bar-group {
    display: flex;
    align-items: center;
    gap: 0.375rem;
  }

  .bar {
    height: 12px;
    background-color: var(--accent);
    border-radius: 2px;
    min-width: 2px;
    transition: width 0.3s ease;
  }

  .bar-value {
    font-size: 0.6875rem;
    color: var(--text-muted);
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  }

  .timeline-legend {
    display: flex;
    gap: 1rem;
    padding: 0.5rem 0.75rem;
    border-top: 1px solid var(--border-light);
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.6875rem;
    color: var(--text-secondary);
  }

  .legend-dot {
    width: 8px;
    height: 8px;
    background-color: var(--accent);
    border-radius: 2px;
  }
</style>
