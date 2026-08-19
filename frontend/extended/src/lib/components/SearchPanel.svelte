<script lang="ts">
  let {
    value,
    disabled = false,
    generatedPrompt = null,
    onSubmit,
    onInput
  }: {
    value: string;
    disabled?: boolean;
    generatedPrompt?: string | null;
    onSubmit: (text: string) => void;
    onInput: (text: string) => void;
  } = $props();

  let textarea: HTMLTextAreaElement;
  let isFocused = $state(false);

  function handleSubmit() {
    if (!value.trim() || disabled) return;
    onSubmit(value);
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  }

  function autoResize() {
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
    }
  }

  function handleInput() {
    onInput(value);
    autoResize();
  }

  $effect(() => {
    value;
    autoResize();
  });
</script>

<div class="search-panel">
  <div
    class="search-wrapper"
    class:focused={isFocused}
    class:has-prompt={generatedPrompt !== null}
  >
    <div class="search-icon">
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"></circle>
        <path d="m21 21-4.3-4.3"></path>
      </svg>
    </div>

    <textarea
      bind:this={textarea}
      bind:value
      onkeydown={handleKeydown}
      oninput={handleInput}
      onfocus={() => { isFocused = true; }}
      onblur={() => { isFocused = false; }}
      placeholder="Ask a question about the scholarly literature..."
      rows="1"
      {disabled}
      aria-label="Research question input"
    ></textarea>

    <button
      class="submit-btn"
      onclick={handleSubmit}
      disabled={!value.trim() || disabled}
      title="Submit question"
    >
      {#if disabled}
        <div class="btn-spinner"></div>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 12h14"></path>
          <path d="m12 5 7 7-7 7"></path>
        </svg>
      {/if}
    </button>
  </div>

  <p class="hint">
    Press <kbd>Enter</kbd> to send, <kbd>Shift + Enter</kbd> for new line
  </p>
</div>

<style>
  .search-panel {
    padding: 0.75rem 1rem;
    background-color: var(--bg-primary);
  }

  .search-wrapper {
    display: flex;
    align-items: flex-end;
    gap: 0.5rem;
    max-width: 900px;
    margin: 0 auto;
    padding: 0.5rem 0.625rem;
    background-color: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 24px;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }

  .search-wrapper.focused {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-light);
  }

  .search-wrapper.has-prompt {
    border-color: var(--accent);
    animation: prompt-pulse 0.5s ease;
  }

  @keyframes prompt-pulse {
    0%, 100% { box-shadow: 0 0 0 3px var(--accent-light); }
    50% { box-shadow: 0 0 0 6px var(--accent-light); }
  }

  .search-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    flex-shrink: 0;
    margin-bottom: 2px;
  }

  textarea {
    flex: 1;
    padding: 0.375rem 0.25rem;
    background-color: transparent;
    border: none;
    color: var(--text-primary);
    font-size: 0.875rem;
    font-family: inherit;
    resize: none;
    outline: none;
    line-height: 1.5;
    max-height: 100px;
  }

  textarea::placeholder {
    color: var(--text-muted);
  }

  textarea:disabled {
    opacity: 0.5;
  }

  .submit-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background-color: var(--accent);
    border: none;
    border-radius: 50%;
    color: white;
    cursor: pointer;
    transition: background-color 0.15s ease;
    flex-shrink: 0;
  }

  .submit-btn:hover:not(:disabled) {
    background-color: var(--accent-hover);
  }

  .submit-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .submit-btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }

  .btn-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .hint {
    text-align: center;
    font-size: 0.6875rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
  }

  kbd {
    padding: 0.0625rem 0.25rem;
    background-color: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 3px;
    font-family: inherit;
    font-size: 0.625rem;
    color: var(--text-secondary);
  }
</style>
