<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import ConversationView from '$lib/components/Conversation/ConversationView.svelte';
  import PromptInput from '$lib/components/Input/PromptInput.svelte';
  import { exploration } from '$lib/stores/exploration.svelte';
  import { decodeStateFromUrl } from '$lib/utils/persistence';

  let initialized = $state(false);

  onMount(() => {
    const urlState = decodeStateFromUrl(page.url.searchParams);

    if (urlState.q) {
      exploration.sendMessage(urlState.q);
    } else {
      exploration.loadState();
    }

    initialized = true;
  });

  let resultsMap = $derived(exploration.resultsByTurn);

  let observationsMap = $derived(exploration.observationsByTurn);

  let suggestionsMap = $derived(exploration.suggestionsByTurn);
</script>

<svelte:head>
  <title>Scholarly Explorer</title>
  <meta name="description" content="Explore scholarly knowledge graphs through conversation" />
</svelte:head>

<div class="app">
  <div class="chat-container">
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
    filtersByTurn={exploration.filtersByTurn}
    sparqlByTurn={exploration.sparqlByTurn}
    statusByTurn={exploration.statusByTurn}
    onRemoveFilter={(f) => exploration.removeFilter(f)}
      onSelectSuggestion={(s) => exploration.selectSuggestion(s)}
    />

    <PromptInput
      onSend={(msg) => exploration.sendMessage(msg)}
      disabled={exploration.loading}
    />
  </div>
</div>

<style>
  .app {
    display: flex;
    flex-direction: column;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    background-color: var(--bg-secondary);
  }

  .chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    max-width: 900px;
    width: 100%;
    margin: 0 auto;
    overflow: hidden;
    background-color: var(--bg-primary);
  }

  .app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.625rem 1rem;
    background-color: var(--bg-primary);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }

  .app-title {
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
  }

  .clear-btn {
    padding: 0.25rem 0.625rem;
    font-size: 0.75rem;
    font-weight: 500;
    font-family: inherit;
    background-color: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border);
    border-radius: 4px;
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

  @media (max-width: 640px) {
    .app-header {
      padding: 0.5rem 0.75rem;
    }

    .app-title {
      font-size: 0.875rem;
    }
  }
</style>
