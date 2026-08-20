<script lang="ts">
  let {
    query
  }: {
    query: string;
  } = $props();

  let copied = $state(false);

  function formatSparql(raw: string): string {
    const keywords = [
      'PREFIX', 'SELECT', 'WHERE', 'GROUP BY', 'ORDER BY', 'LIMIT',
      'FILTER', 'HAVING', 'UNION', 'OPTIONAL', 'BIND', 'VALUES', 'CONSTRUCT',
      'ASK', 'DESCRIBE', 'INSERT', 'DELETE', 'WITH', 'USING', 'GRAPH'
    ];

    let formatted = raw.trim();

    for (const keyword of keywords) {
      const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
      formatted = formatted.replace(regex, `\n${keyword}`);
    }

    formatted = formatted.replace(/\{/g, ' {\n  ');
    formatted = formatted.replace(/\}/g, '\n}');
    formatted = formatted.replace(/;\n\s*$/gm, ' ;');
    formatted = formatted.replace(/\.\n/g, ' .\n');

    const lines = formatted.split('\n');
    const result: string[] = [];
    let indent = 0;

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;

      if (trimmed === '}') {
        indent = Math.max(0, indent - 1);
      }

      result.push('  '.repeat(indent) + trimmed);

      if (trimmed.endsWith('{') || trimmed === '{') {
        indent++;
      }
    }

    return result.join('\n').trim();
  }

  let formattedQuery = $derived(formatSparql(query));

  async function copyToClipboard(): Promise<void> {
    try {
      await navigator.clipboard.writeText(query);
      copied = true;
      setTimeout(() => { copied = false; }, 2000);
    } catch {
      const textarea = document.createElement('textarea');
      textarea.value = query;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      copied = true;
      setTimeout(() => { copied = false; }, 2000);
    }
  }
</script>

<div class="sparql-block">
  <button
    class="copy-btn"
    onclick={copyToClipboard}
    title={copied ? 'Copied!' : 'Copy to clipboard'}
    aria-label={copied ? 'Copied!' : 'Copy SPARQL query to clipboard'}
  >
    {#if copied}
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
    {:else}
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect>
        <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path>
      </svg>
    {/if}
  </button>
  <pre class="sparql-code"><code>{formattedQuery}</code></pre>
</div>

<style>
  .sparql-block {
    position: relative;
    padding: 0.75rem;
    background-color: var(--code-bg);
    border-top: 1px solid var(--code-border);
  }

  .copy-btn {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background-color: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: background-color 0.15s ease, color 0.15s ease;
    z-index: 1;
    padding: 0;
  }

  .copy-btn:hover {
    background-color: var(--accent-light);
    color: var(--accent);
    border-color: var(--accent);
  }

  .copy-btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }

  .sparql-code {
    margin: 0;
    padding: 0;
    background: transparent;
    border: none;
    overflow-x: auto;
    white-space: pre;
  }

  .sparql-code code {
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 0.75rem;
    color: var(--text-primary);
    line-height: 1.6;
  }
</style>
