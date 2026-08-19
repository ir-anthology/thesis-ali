<script lang="ts">
  import type { LoadingStage } from '$lib/types/exploration';

  let { stage }: { stage: LoadingStage } = $props();

  const stageLabels: Record<string, string> = {
    interpreting: 'Interpreting question...',
    preparing: 'Preparing search...',
    querying: 'Querying scholarly data...',
    analyzing: 'Analyzing results...'
  };

  const stageProgress: Record<string, number> = {
    interpreting: 25,
    preparing: 50,
    querying: 75,
    analyzing: 95
  };
</script>

{#if stage}
  <div class="loading-state" role="status" aria-live="polite">
    <div class="loading-content">
      <div class="spinner"></div>
      <span class="loading-text">{stageLabels[stage] || 'Processing...'}</span>
    </div>
    <div class="progress-bar">
      <div
        class="progress-fill"
        style="width: {stageProgress[stage] || 0}%"
      ></div>
    </div>
  </div>
{/if}

<style>
  .loading-state {
    padding: 1rem;
    background-color: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 0.5rem;
  }

  .loading-content {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    margin-bottom: 0.75rem;
  }

  .spinner {
    width: 18px;
    height: 18px;
    border: 2px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  .loading-text {
    font-size: 0.875rem;
    color: var(--text-secondary);
  }

  .progress-bar {
    height: 4px;
    background-color: var(--bg-tertiary);
    border-radius: 2px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background-color: var(--accent);
    border-radius: 2px;
    transition: width 0.4s ease;
  }
</style>
