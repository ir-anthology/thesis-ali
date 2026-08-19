<script lang="ts">
  import Pill from '$lib/components/Shared/Pill.svelte';

  let {
    filters,
    onRemove
  }: {
    filters: { facet: string; value: string; label: string }[];
    onRemove: (filter: { facet: string; value: string; label: string }) => void;
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
