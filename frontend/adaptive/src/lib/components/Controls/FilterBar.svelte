<script lang="ts">
  import type { Filter } from '$lib/types/exploration';
  import Pill from '$lib/components/Shared/Pill.svelte';

  let {
    filters,
    onRemove
  }: {
    filters: Filter[];
    onRemove: (filter: Filter) => void;
  } = $props();
</script>

{#if filters.length > 0}
  <div class="filter-bar">
    {#each filters as filter (filter.facet + filter.value)}
      <Pill label="{filter.facet}: {filter.label}" onRemove={() => onRemove(filter)} />
    {/each}
  </div>
{/if}

<style>
  .filter-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 0.375rem;
    margin-top: 0.625rem;
    padding-bottom: 0.375rem;
  }
</style>
