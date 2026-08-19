<script lang="ts">
  let { size = 16 }: { size?: number } = $props();
</script>

<div class="spinner" style="width: {size}px; height: {size}px;" role="status" aria-label="Loading">
  <span class="sr-only">Loading...</span>
</div>

<style>
  .spinner {
    border: 2px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
  }
</style>
