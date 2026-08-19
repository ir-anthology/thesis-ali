<script lang="ts">
  let {
    promptOutputMode,
    onToggleMode
  }: {
    promptOutputMode: 'input' | 'tooltip';
    onToggleMode: () => void;
  } = $props();
</script>

<header class="header">
  <div class="header-content">
    <div class="header-left">
      <div class="logo">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"></path>
          <path d="M2 12h20"></path>
        </svg>
      </div>
      <div class="title-group">
        <h1 class="title">Scholarly Explorer</h1>
        <p class="subtitle">LLM-Assisted Exploratory Search in Scholarly Knowledge Graphs</p>
      </div>
    </div>

    <div class="header-right">
      <button
        class="settings-btn"
        onclick={onToggleMode}
        aria-label="Toggle prompt output mode"
        aria-pressed={promptOutputMode === 'tooltip'}
        title="Prompt output: {promptOutputMode === 'tooltip' ? 'Tooltip' : 'Input box'}"
      >
        {#if promptOutputMode === 'tooltip'}
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            <circle cx="12" cy="10" r="0.5" fill="currentColor"></circle>
            <circle cx="8" cy="10" r="0.5" fill="currentColor"></circle>
            <circle cx="16" cy="10" r="0.5" fill="currentColor"></circle>
          </svg>
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="18" height="18" x="3" y="3" rx="2"></rect>
            <path d="M7 7h10"></path>
            <path d="M7 12h10"></path>
            <path d="M7 17h4"></path>
          </svg>
        {/if}
      </button>
    </div>
  </div>
</header>

<style>
  .header {
    background-color: var(--bg-primary);
    border-bottom: 1px solid var(--border);
    padding: 0.75rem 1rem;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1200px;
    margin: 0 auto;
    gap: 1rem;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 0;
  }

  .logo {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background-color: var(--accent);
    color: white;
    border-radius: 8px;
    flex-shrink: 0;
  }

  .title-group {
    min-width: 0;
  }

  .title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
    line-height: 1.2;
  }

  .subtitle {
    font-size: 0.75rem;
    color: var(--text-muted);
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-shrink: 0;
  }

  .settings-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    padding: 0;
    background-color: transparent;
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .settings-btn:hover {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    border-color: var(--text-muted);
  }

  .settings-btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }

  .settings-btn[aria-pressed="true"] {
    background-color: var(--accent-light);
    border-color: var(--accent);
    color: var(--accent);
  }

  @media (max-width: 640px) {
    .subtitle {
      display: none;
    }
  }
</style>
