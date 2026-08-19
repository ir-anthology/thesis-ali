<script lang="ts">
  import type { Observation } from '$lib/types/exploration';
  import Badge from '$lib/components/Shared/Badge.svelte';

  let { observation }: { observation: Observation } = $props();
</script>

<div class="observation-card">
  <div class="observation-header">
    <Badge variant="accent">AI</Badge>
    <span class="observation-label">Interpretation</span>
  </div>
  <p class="observation-text">{observation.text}</p>
</div>

<style>
  .observation-card {
    padding: 0.75rem 1rem;
    background-color: var(--ai-interpretation-bg);
    border-left: 3px solid var(--ai-interpretation-border);
    border-radius: 0 6px 6px 0;
    margin-top: 0.625rem;
  }

  .observation-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.375rem;
  }

  .observation-label {
    font-size: 0.6875rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .observation-text {
    font-size: 0.8125rem;
    color: var(--text-primary);
    line-height: 1.5;
    margin: 0;
  }
</style>
