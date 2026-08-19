<script>
  let { onSend, disabled = false } = $props();

  let inputValue = $state('');
  let textarea;

  function handleSubmit() {
    if (!inputValue.trim() || disabled) return;
    onSend(inputValue);
    inputValue = '';
    resetTextareaHeight();
  }

  function handleKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  }

  function autoResize() {
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
    }
  }

  function resetTextareaHeight() {
    if (textarea) {
      textarea.style.height = 'auto';
    }
  }

  $effect(() => {
    inputValue;
    autoResize();
  });
</script>

<div class="input-container">
  <div class="input-wrapper">
    <textarea
      bind:this={textarea}
      bind:value={inputValue}
      onkeydown={handleKeydown}
      placeholder="Ask for a SPARQL query..."
      rows="1"
      {disabled}
    ></textarea>

    <button
      class="send-btn"
      onclick={handleSubmit}
      disabled={!inputValue.trim() || disabled}
      title="Send message"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="m22 2-7 20-4-9-9-4Z"></path>
        <path d="M22 2 11 13"></path>
      </svg>
    </button>
  </div>

  <p class="hint">
    Press <kbd>Enter</kbd> to send, <kbd>Shift + Enter</kbd> for new line
  </p>
</div>

<style>
  .input-container {
    padding: 0.75rem 1rem;
    background-color: var(--bg-primary);
    border-top: 1px solid var(--border);
  }

  .input-wrapper {
    display: flex;
    align-items: flex-end;
    gap: 0.5rem;
    max-width: 900px;
    margin: 0 auto;
    padding: 0.5rem 0.625rem;
    background-color: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 8px;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }

  .input-wrapper:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-light);
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
    max-height: 150px;
  }

  textarea::placeholder {
    color: var(--text-muted);
  }

  textarea:disabled {
    opacity: 0.5;
  }

  .send-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background-color: var(--accent);
    border: none;
    border-radius: 6px;
    color: white;
    cursor: pointer;
    transition: background-color 0.15s ease;
    flex-shrink: 0;
  }

  .send-btn:hover:not(:disabled) {
    background-color: var(--accent-hover);
  }

  .send-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .send-btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }

  .hint {
    text-align: center;
    font-size: 0.6875rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
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
