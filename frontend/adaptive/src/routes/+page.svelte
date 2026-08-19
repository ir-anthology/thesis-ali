<script lang="ts">
  import ConversationView from '$lib/components/Conversation/ConversationView.svelte';
  import PromptInput from '$lib/components/Input/PromptInput.svelte';
  import { exploration } from '$lib/stores/exploration.svelte';

  let resultsMap = $derived.by(() => {
    const map = new Map();
    const assistantTurns = exploration.conversation.filter(
      (t) => t.role === 'assistant' && !t.loading
    );
    if (assistantTurns.length > 0 && exploration.result) {
      map.set(assistantTurns[assistantTurns.length - 1].id, exploration.result);
    }
    return map;
  });

  let observationsMap = $derived.by(() => {
    const map = new Map();
    const assistantTurns = exploration.conversation.filter(
      (t) => t.role === 'assistant' && !t.loading
    );
    if (assistantTurns.length > 0 && exploration.observations.length > 0) {
      map.set(assistantTurns[assistantTurns.length - 1].id, exploration.observations);
    }
    return map;
  });

  let suggestionsMap = $derived.by(() => {
    const map = new Map();
    const assistantTurns = exploration.conversation.filter(
      (t) => t.role === 'assistant' && !t.loading
    );
    if (assistantTurns.length > 0 && exploration.suggestions.length > 0) {
      map.set(assistantTurns[assistantTurns.length - 1].id, exploration.suggestions);
    }
    return map;
  });
</script>

<svelte:head>
  <title>Scholarly Explorer</title>
  <meta name="description" content="Explore scholarly knowledge graphs through conversation" />
</svelte:head>

<div class="app">
  <header class="app-header">
    <h1 class="app-title">Scholarly Explorer</h1>
    {#if exploration.conversation.length > 0}
      <button class="clear-btn" onclick={() => exploration.clearExploration()}>
        New Exploration
      </button>
    {/if}
  </header>

  <ConversationView
    conversation={exploration.conversation}
    results={resultsMap}
    observations={observationsMap}
    suggestions={suggestionsMap}
    filters={exploration.filters}
    onRemoveFilter={(f) => exploration.removeFilter(f)}
    onSelectSuggestion={(s) => exploration.selectSuggestion(s)}
  />

  <PromptInput
    onSend={(msg) => exploration.sendMessage(msg)}
    disabled={exploration.loading}
  />
</div>

<style>
  .app {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
  }

  .app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    background-color: var(--bg-primary);
    border-bottom: 1px solid var(--border);
  }

  .app-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
  }

  .clear-btn {
    padding: 0.3125rem 0.75rem;
    font-size: 0.8125rem;
    font-weight: 500;
    font-family: inherit;
    background-color: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border);
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.15s ease, color 0.15s ease;
  }

  .clear-btn:hover {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
  }

  .clear-btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
</style>
