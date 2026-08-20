<script lang="ts">
  import type { ResultState } from '$lib/types/exploration';
  import FacetTable from './FacetTable.svelte';

  let { result }: { result: ResultState } = $props();
</script>

{#if result.columns.length > 0}
  <FacetTable columns={result.columns} rows={result.rows} />
{/if}
