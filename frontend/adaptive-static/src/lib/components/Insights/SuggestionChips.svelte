<script lang="ts">
  let {
    suggestions,
    onSelect
  }: {
    suggestions: string[];
    onSelect: (suggestion: string) => void;
  } = $props();
</script>

{#if suggestions.length > 0}
  <div class="suggestions" role="group" aria-label="Suggested follow-up questions">
    <div class="suggestions-list">
      {#each suggestions as suggestion, i (i)}
        <button
          class="suggestion-chip"
          onclick={() => onSelect(suggestion)}
          aria-label="Ask: {suggestion}"
        >
          {suggestion}
        </button>
      {/each}
    </div>
  </div>
{/if}

<style>
  .suggestions {
    margin-top: 0.75rem;
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
