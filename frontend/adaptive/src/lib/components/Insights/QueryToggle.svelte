<script lang="ts">
  let {
    naturalLanguage,
    sparqlQuery
  }: {
    naturalLanguage: string;
    sparqlQuery: string;
  } = $props();

  let activeTab = $state<'nl' | 'sparql'>('nl');
  let copied = $state(false);

  function formatSparql(query: string): string {
    const keywords = [
      'PREFIX', 'SELECT', 'WHERE', 'GROUP BY', 'ORDER BY', 'LIMIT',
      'FILTER', 'HAVING', 'UNION', 'OPTIONAL', 'BIND', 'VALUES', 'CONSTRUCT',
      'ASK', 'DESCRIBE', 'INSERT', 'DELETE', 'WITH', 'USING', 'GRAPH'
    ];

    let formatted = query.trim();

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

  let formattedQuery = $derived(formatSparql(sparqlQuery));

  async function copyToClipboard(): Promise<void> {
    try {
      await navigator.clipboard.writeText(sparqlQuery);
      copied = true;
      setTimeout(() => { copied = false; }, 2000);
    } catch {
      const textarea = document.createElement('textarea');
      textarea.value = sparqlQuery;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      copied = true;
      setTimeout(() => { copied = false; }, 2000);
    }
  }
</script>

<div class="query-toggle">
  <div class="toggle-tabs" role="tablist" aria-label="Query view">
    <button
      class="toggle-tab"
      class:active={activeTab === 'nl'}
      onclick={() => activeTab = 'nl'}
      role="tab"
      aria-selected={activeTab === 'nl'}
      aria-controls="nl-panel"
    >
      Natural Language
    </button>
    <button
      class="toggle-tab"
      class:active={activeTab === 'sparql'}
      onclick={() => activeTab = 'sparql'}
      role="tab"
      aria-selected={activeTab === 'sparql'}
      aria-controls="sparql-panel"
    >
      SPARQL Query
    </button>
  </div>

  {#if activeTab === 'nl'}
    <div class="toggle-content nl-content" id="nl-panel" role="tabpanel">
      <p>{naturalLanguage}</p>
    </div>
  {:else}
    <div class="toggle-content sparql-content" id="sparql-panel" role="tabpanel">
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
  {/if}
</div>

<style>
  .query-toggle {
    margin-top: 0.625rem;
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
  }

  .toggle-tabs {
    display: flex;
    border-bottom: 1px solid var(--border);
    background-color: var(--bg-secondary);
  }

  .toggle-tab {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 500;
    font-family: inherit;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-secondary);
    cursor: pointer;
    transition: color 0.15s ease, border-color 0.15s ease, background-color 0.15s ease;
  }

  .toggle-tab:hover {
    color: var(--text-primary);
    background-color: var(--bg-tertiary);
  }

  .toggle-tab.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
    background-color: var(--bg-primary);
  }

  .toggle-tab:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: -2px;
  }

  .toggle-content {
    padding: 0.625rem 0.75rem;
    background-color: var(--bg-primary);
  }

  .nl-content p {
    margin: 0;
    font-size: 0.875rem;
    color: var(--text-primary);
    line-height: 1.5;
  }

  .sparql-content {
    position: relative;
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
