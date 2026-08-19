<script lang="ts">
  import type { ResultState } from '$lib/types/exploration';
  import FacetTable from './FacetTable.svelte';
  import ComparisonView from './ComparisonView.svelte';
  import TimelineView from './TimelineView.svelte';
  import SummaryView from './SummaryView.svelte';

  let { result }: { result: ResultState } = $props();
</script>

{#if result.type === 'facet_table' || result.type === 'entity_list'}
  <FacetTable columns={result.columns} rows={result.rows} title={result.title} />
{:else if result.type === 'comparison'}
  <ComparisonView columns={result.columns} rows={result.rows} title={result.title} />
{:else if result.type === 'timeline'}
  <TimelineView columns={result.columns} rows={result.rows} title={result.title} />
{:else if result.type === 'summary'}
  <SummaryView title={result.title} />
{/if}
