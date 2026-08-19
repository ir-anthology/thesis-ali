<script lang="ts">
  let {
    text,
    onClick
  }: {
    text: string;
    onClick: () => void;
  } = $props();
</script>

<button class="follow-up-button" onclick={onClick} aria-label="Ask: {text}">
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="m21 15-3-3v-3.36c0-.53-.4-.96-.9-.96L12 7.76"></path>
    <path d="M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z"></path>
    <path d="M8 12h.01"></path>
    <path d="M12 12h.01"></path>
    <path d="M16 12h.01"></path>
  </svg>
  <span class="follow-up-text">{text}</span>
  <svg class="follow-up-arrow" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M5 12h14"></path>
    <path d="m12 5 7 7-7 7"></path>
  </svg>
</button>

<style>
  .follow-up-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
    padding: 0.5rem 0.75rem;
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 6px;
    text-align: left;
    font-size: 0.8125rem;
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .follow-up-button:hover {
    border-color: var(--accent);
    background-color: var(--accent-light);
  }

  .follow-up-button:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }

  .follow-up-button:active {
    background-color: var(--cell-active);
  }

  .follow-up-arrow {
    flex-shrink: 0;
    margin-left: auto;
    color: var(--text-muted);
    transition: transform 0.15s ease;
  }

  .follow-up-button:hover .follow-up-arrow {
    transform: translateX(2px);
    color: var(--accent);
  }
</style>
