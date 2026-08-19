<script lang="ts">
  import FollowUpButton from './FollowUpButton.svelte';

  let {
    suggestions,
    onSuggestionClick
  }: {
    suggestions: string[];
    onSuggestionClick: (text: string) => void;
  } = $props();
</script>

<div class="unsupported-state" role="alert">
  <div class="state-icon">
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="12" x2="12" y1="8" y2="12"></line>
      <line x1="12" x2="12.01" y1="16" y2="16"></line>
    </svg>
  </div>

  <div class="state-content">
    <h3>This question cannot currently be answered</h3>
    <p>using the available scholarly data.</p>
  </div>

  {#if suggestions.length > 0}
    <div class="suggestions">
      <p class="suggestions-label">You could try:</p>
      <div class="suggestions-list">
        {#each suggestions as suggestion}
          <FollowUpButton text={suggestion} onClick={() => onSuggestionClick(suggestion)} />
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .unsupported-state {
    padding: 1.25rem;
    background-color: var(--bg-primary);
    border: 1px solid var(--warning);
    border-radius: 8px;
    margin-bottom: 0.5rem;
  }

  .state-icon {
    color: var(--warning);
    margin-bottom: 0.75rem;
  }

  .state-content {
    margin-bottom: 1rem;
  }

  .state-content h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
  }

  .state-content p {
    font-size: 0.875rem;
    color: var(--text-secondary);
  }

  .suggestions-label {
    font-size: 0.8125rem;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
  }

  .suggestions-list {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
  }
</style>
