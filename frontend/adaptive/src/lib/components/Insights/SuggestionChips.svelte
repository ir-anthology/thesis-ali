<script lang="ts">
  import type { FollowUpQuestion } from '$lib/types/exploration';

  let {
    suggestions,
    onSelect
  }: {
    suggestions: FollowUpQuestion[];
    onSelect: (suggestion: FollowUpQuestion) => void;
  } = $props();
</script>

{#if suggestions.length > 0}
  <div class="suggestions">
    <p class="suggestions-label">You could explore:</p>
    <div class="suggestions-list">
      {#each suggestions as suggestion (suggestion.id)}
        <button class="suggestion-chip" onclick={() => onSelect(suggestion)}>
          {suggestion.text}
        </button>
      {/each}
    </div>
  </div>
{/if}

<style>
  .suggestions {
    margin-top: 0.75rem;
  }

  .suggestions-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
  }

  .suggestions-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.375rem;
  }

  .suggestion-chip {
    padding: 0.3125rem 0.75rem;
    font-size: 0.8125rem;
    font-family: inherit;
    background-color: transparent;
    color: var(--accent);
    border: 1px solid var(--border);
    border-radius: 9999px;
    cursor: pointer;
    transition: background-color 0.15s ease, border-color 0.15s ease;
    white-space: nowrap;
  }

  .suggestion-chip:hover {
    background-color: var(--accent-light);
    border-color: var(--accent);
  }

  .suggestion-chip:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
</style>
