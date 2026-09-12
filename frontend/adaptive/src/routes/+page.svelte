<script lang="ts">
  import ConversationView from '$lib/components/Conversation/ConversationView.svelte';
  import PromptInput from '$lib/components/Input/PromptInput.svelte';
  import { exploration } from '$lib/stores/exploration.svelte';
</script>

<svelte:head>
  <title>IR Anthology Chat</title>
  <meta name="description" content="Explore the IR Anthology knowledge graph through conversation" />
</svelte:head>

<div class="app">
  <nav class="w-full relative z-10" style="background: linear-gradient(to bottom, #f8f9fa, #e9ecef); box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1);">
    <div class="w-full h-17.5 flex items-center justify-between" style="padding: 0 1.5rem;">
      <div class="flex items-center gap-4">
        <a class="flex items-center h-10 text-xl font-normal text-black/90 no-underline" href="./">
          <span><span style="color:#951515"><b>IR</b></span> Anthology</span>
        </a>
      </div>
      {#if exploration.conversation.length > 0}
        <button class="new-explo-btn" onclick={() => exploration.clearExploration()}>
          New Exploration
        </button>
      {/if}
    </div>
  </nav>

  <div class="chat-container">
    <ConversationView
      conversation={exploration.conversation}
      interpretationByTurn={exploration.interpretationByTurn}
      columnsByTurn={exploration.columnsByTurn}
      rowsByTurn={exploration.rowsByTurn}
      observationsByTurn={exploration.observationsByTurn}
      suggestionsByTurn={exploration.suggestionsByTurn}
      sparqlByTurn={exploration.sparqlByTurn}
      onSelectSuggestion={(s, fromTurnId) => exploration.selectSuggestion(s, fromTurnId)}
      activePath={exploration.getActivePath()}
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
    position: relative;
    z-index: 1;
  }

  .new-explo-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
    font-weight: 500;
    font-family: inherit;
    background-color: white;
    color: #374151;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    border: 1px solid #d1d5db;
    cursor: pointer;
    transition: background-color 0.15s ease;
  }

  .new-explo-btn:hover {
    background-color: #f9fafb;
  }

  .new-explo-btn:focus-visible {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
  }
</style>
