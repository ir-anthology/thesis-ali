<script>
  import { chatStore } from '$lib/stores/chat.svelte';

  function handleClear() {
    chatStore.clearMessages();
  }
</script>

<header class="header">
  <div class="header-content">
    <div class="logo">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      </svg>
      <h1>SPARQL Chat</h1>
    </div>

    <div class="actions">
      <button class="clear-btn" onclick={handleClear} title="Clear chat">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M3 6h18"></path>
          <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
          <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
        </svg>
        Clear
      </button>
    </div>
  </div>
</header>

<style>
  .header {
    background-color: var(--bg-primary);
    border-bottom: 1px solid var(--border);
    padding: 0.625rem 1rem;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 900px;
    margin: 0 auto;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .logo h1 {
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
  }

  .clear-btn {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.625rem;
    background-color: transparent;
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--text-secondary);
    font-size: 0.8125rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .clear-btn:hover {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    border-color: var(--text-muted);
  }

  .clear-btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
</style>
