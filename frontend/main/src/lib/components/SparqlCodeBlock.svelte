<script>
  let { code, onExecute } = $props();

  let copied = $state(false);
  let isEditing = $state(false);
  let editedCode = $state('');

  function startEdit() {
    editedCode = code;
    isEditing = true;
  }

  function revertEdit() {
    editedCode = code;
    isEditing = false;
  }

  function handleKeydown(event) {
    if (event.key === 'Escape') {
      revertEdit();
    }
  }

  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(isEditing ? editedCode : code);
      copied = true;
      setTimeout(() => {
        copied = false;
      }, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }

  function handleExecute() {
    if (onExecute) {
      onExecute(isEditing ? editedCode : code);
      isEditing = false;
    }
  }
</script>

<div class="code-container">
  <div class="code-header">
    <span class="language-tag">SPARQL</span>
    <div class="header-actions">
      <button class="icon-btn" onclick={copyToClipboard} title="Copy to clipboard">
        {#if copied}
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 6 9 17l-5-5"></path>
          </svg>
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect>
            <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path>
          </svg>
        {/if}
      </button>

      {#if isEditing}
        <button class="icon-btn" onclick={revertEdit} title="Revert changes">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 7v6h6"></path>
            <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"></path>
          </svg>
        </button>
      {:else}
        <button class="icon-btn" onclick={startEdit} title="Edit query">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"></path>
            <path d="m15 5 4 4"></path>
          </svg>
        </button>
      {/if}
    </div>
  </div>

  <div class="code-body">
    <pre class="code-block"><code>{code}</code></pre>
    {#if isEditing}
      <textarea class="code-editor" bind:value={editedCode} spellcheck="false" onkeydown={handleKeydown}></textarea>
    {/if}
  </div>

  {#if onExecute}
    <div class="code-footer">
      <button class="execute-btn" onclick={handleExecute} title="Execute query">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        Execute
      </button>
    </div>
  {/if}
</div>

<style>
  .code-container {
    margin-top: 0.625rem;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--code-border);
  }

  .code-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.375rem 0.625rem;
    background-color: var(--bg-secondary);
    border-bottom: 1px solid var(--code-border);
  }

  .language-tag {
    font-size: 0.6875rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .icon-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    padding: 0;
    background-color: transparent;
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .icon-btn:hover {
    background-color: var(--bg-tertiary);
    color: var(--text-primary);
  }

  .icon-btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }

  .code-block {
    margin: 0;
    padding: 0.75rem;
    background-color: var(--code-bg);
    overflow-x: auto;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 0.8125rem;
    line-height: 1.6;
    color: var(--text-primary);
  }

  .code-block code {
    white-space: pre;
  }

  .code-body {
    position: relative;
  }

  .code-editor {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0.75rem;
    background-color: var(--code-bg);
    border: none;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 0.8125rem;
    line-height: 1.6;
    color: var(--text-primary);
    outline: none;
    tab-size: 2;
    resize: none;
    overflow: auto;
    box-sizing: border-box;
  }

  .code-editor:focus {
    box-shadow: inset 0 0 0 2px var(--accent);
  }

  .code-footer {
    padding: 0.375rem 0.625rem;
    background-color: var(--bg-secondary);
    border-top: 1px solid var(--code-border);
  }

  .execute-btn {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.3125rem 0.625rem;
    background-color: var(--accent);
    border: none;
    border-radius: 4px;
    color: white;
    font-size: 0.75rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.15s ease;
  }

  .execute-btn:hover {
    background-color: var(--accent-hover);
  }

  .execute-btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
</style>
