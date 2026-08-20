<script lang="ts">
  import type { Observation } from '$lib/types/exploration';

  let { observation }: { observation: Observation } = $props();
</script>

<p class="observation-text">{observation.text}</p>

<style>
  .observation-text {
    font-size: 0.875rem;
    color: var(--text-primary);
    line-height: 1.5;
    margin: 0;
  }
</style>
