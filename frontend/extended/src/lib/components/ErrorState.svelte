<script lang="ts">
  import type { ErrorState } from '$lib/types/exploration';

  let {
    error,
    onRetry
  }: {
    error: ErrorState;
    onRetry: () => void;
  } = $props();
</script>

<div class="error-state" role="alert">
  <div class="error-icon">
    {#if error.type === 'unavailable'}
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
        <line x1="12" x2="12" y1="9" y2="13"></line>
        <line x1="12" x2="12.01" y1="17" y2="17"></line>
      </svg>
    {:else}
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="15" x2="9" y1="9" y2="15"></line>
        <line x1="9" x2="15" y1="9" y2="15"></line>
      </svg>
    {/if}
  </div>

  <div class="error-content">
    <h3>Something went wrong</h3>
    <p>{error.message}</p>
  </div>

  <button class="retry-button" onclick={onRetry}>
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>
      <path d="M21 3v5h-5"></path>
      <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>
      <path d="M8 16H3v5"></path>
    </svg>
    Try again
  </button>
</div>

<style>
  .error-state {
    padding: 1.25rem;
    background-color: var(--bg-primary);
    border: 1px solid var(--error);
    border-radius: 8px;
    margin-bottom: 0.5rem;
  }

  .error-icon {
    color: var(--error);
    margin-bottom: 0.75rem;
  }

  .error-content {
    margin-bottom: 1rem;
  }

  .error-content h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
  }

  .error-content p {
    font-size: 0.875rem;
    color: var(--text-secondary);
  }

  .retry-button {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.5rem 1rem;
    background-color: transparent;
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text-primary);
    font-size: 0.8125rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .retry-button:hover {
    background-color: var(--bg-secondary);
    border-color: var(--text-muted);
  }

  .retry-button:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
</style>
