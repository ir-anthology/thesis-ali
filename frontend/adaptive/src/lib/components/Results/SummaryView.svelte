<script lang="ts">
  let { title }: { title?: string } = $props();
</script>

{#if title}
  <div class="summary-container">
    <p class="summary-text">{title}</p>
  </div>
{/if}

<style>
  .summary-container {
    margin-top: 0.625rem;
    padding: 0.75rem 1rem;
    background-color: var(--bg-primary);
    border: 1px solid var(--border-light);
    border-radius: 6px;
  }

  .summary-text {
    font-size: 0.8125rem;
    color: var(--text-primary);
    line-height: 1.5;
    margin: 0;
  }
</style>
