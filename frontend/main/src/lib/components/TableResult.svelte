<script>
  let { table } = $props();

  function parseMarkdownTable(markdown) {
    const lines = markdown.trim().split('\n');
    if (lines.length < 2) return { headers: [], rows: [] };

    const parseRow = (line) => {
      return line
        .split('|')
        .map((cell) => cell.trim())
        .filter((cell) => cell !== '');
    };

    const headers = parseRow(lines[0]);
    const rows = [];

    for (let i = 2; i < lines.length; i++) {
      const row = parseRow(lines[i]);
      if (row.length > 0) {
        rows.push(row);
      }
    }

    return { headers, rows };
  }

  let parsed = $derived(parseMarkdownTable(table));
</script>

<div class="table-container">
  <div class="table-header">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
      <line x1="3" x2="21" y1="9" y2="9"></line>
      <line x1="3" x2="21" y1="15" y2="15"></line>
      <line x1="9" x2="9" y1="3" y2="21"></line>
      <line x1="15" x2="15" y1="3" y2="21"></line>
    </svg>
    <span>Query Results</span>
  </div>

  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          {#each parsed.headers as header}
            <th>{header}</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each parsed.rows as row}
          <tr>
            {#each row as cell}
              <td>{cell}</td>
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
</style>
