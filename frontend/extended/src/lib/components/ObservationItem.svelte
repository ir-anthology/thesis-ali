<script lang="ts">
  let { text }: { text: string } = $props();
</script>

<div class="observation-item">
  <span class="observation-icon">
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="12" x2="12" y1="8" y2="12"></line>
      <line x1="12" x2="12.01" y1="16" y2="16"></line>
    </svg>
  </span>
  <span class="observation-text">{text}</span>
</div>

<style>
  .observation-item {
    display: flex;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    background-color: var(--observation-bg);
    border-left: 3px solid var(--accent);
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }

  .observation-icon {
    flex-shrink: 0;
    color: var(--accent);
    margin-top: 1px;
  }

  .observation-text {
    font-size: 0.8125rem;
    color: var(--text-secondary);
    line-height: 1.5;
  }
</style>
