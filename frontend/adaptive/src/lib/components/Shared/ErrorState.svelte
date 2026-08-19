<script lang="ts">
  let {
    message = 'Something went wrong.',
    onRetry
  }: {
    message?: string;
    onRetry?: () => void;
  } = $props();
</script>

<div class="error-state">
  <p class="error-message">{message}</p>
  {#if onRetry}
    <button class="retry-btn" onclick={onRetry}>Retry</button>
  {/if}
</div>

<style>
  .error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
  }

  .error-message {
    color: var(--error);
    font-size: 0.875rem;
    text-align: center;
  }

  .retry-btn {
    padding: 0.375rem 1rem;
    font-size: 0.8125rem;
    font-weight: 500;
    font-family: inherit;
    background-color: transparent;
    color: var(--accent);
    border: 1px solid var(--accent);
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.15s ease, color 0.15s ease;
  }

  .retry-btn:hover {
    background-color: var(--accent);
    color: white;
  }
</style>
