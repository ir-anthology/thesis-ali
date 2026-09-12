<script lang="ts">
  let { text }: { text: string } = $props();
</script>

<p class="observation-text">{text}</p>

<style>
  .observation-text {
    font-size: 0.875rem;
    color: var(--text-primary);
    line-height: 1.5;
    margin: 0.625rem 0 0 0;
  }
</style>
