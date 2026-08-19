<script>
  import ChatHeader from '$lib/components/ChatHeader.svelte';
  import ChatMessage from '$lib/components/ChatMessage.svelte';
  import ChatInput from '$lib/components/ChatInput.svelte';
  import { chatStore } from '$lib/stores/chat.svelte';

  let chatContainer;

  function scrollToBottom() {
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  $effect(() => {
    chatStore.messages;
    scrollToBottom();
  });
</script>

<svelte:head>
  <title>SPARQL Chat</title>
  <meta name="description" content="Generate SPARQL queries using natural language" />
</svelte:head>

<div class="app">
  <ChatHeader />

  <main class="chat-container" bind:this={chatContainer}>
    {#if chatStore.messages.length === 0}
      <div class="welcome">
        <div class="welcome-icon">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        </div>
        <h2>Welcome to SPARQL Chat</h2>
        <p>Ask me to generate SPARQL queries for DBLP publications.</p>
        <div class="examples">
          <p class="example-title">Try asking:</p>
          <ul>
            <li>"List all publications from 2023"</li>
            <li>"Find authors who published in SIGMOD"</li>
            <li>"Show me publications with their venues and years"</li>
          </ul>
        </div>
      </div>
    {:else}
      {#each chatStore.messages as message (message.id)}
        <ChatMessage {message} onExecute={(sparql) => chatStore.sendMessage(sparql)} />
      {/each}
    {/if}
  </main>

  <ChatInput onSend={(msg) => chatStore.sendMessage(msg)} disabled={chatStore.isLoading} />
</div>

<style>
  .app {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
  }

  .chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    background-color: var(--bg-secondary);
  }

  .welcome {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    padding: 1.5rem;
  }

  .welcome-icon {
    color: var(--accent);
    margin-bottom: 0.75rem;
    opacity: 0.8;
  }

  .welcome h2 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.375rem;
    letter-spacing: -0.01em;
  }

  .welcome p {
    color: var(--text-secondary);
    max-width: 320px;
    font-size: 0.875rem;
  }

  .examples {
    margin-top: 1.5rem;
    padding: 0.875rem;
    background-color: var(--bg-primary);
    border-radius: 6px;
    border: 1px solid var(--border);
    text-align: left;
    max-width: 320px;
  }

  .example-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .examples ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .examples li {
    padding: 0.3125rem 0;
    font-size: 0.8125rem;
    color: var(--text-secondary);
    cursor: pointer;
    transition: color 0.15s ease;
  }

  .examples li:hover {
    color: var(--accent);
  }

  @media (max-width: 640px) {
    .chat-container {
      padding: 0.75rem;
    }

    .welcome {
      padding: 1rem;
    }

    .welcome h2 {
      font-size: 1rem;
    }

    .examples {
      max-width: 100%;
    }
  }
</style>
