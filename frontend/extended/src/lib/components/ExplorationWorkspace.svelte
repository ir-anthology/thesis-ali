<script lang="ts">
  let { children }: { children: any } = $props();
</script>

<div class="exploration-workspace">
  <div class="workspace-left">
    {@render children.left()}
  </div>
  <div class="workspace-right">
    {@render children.right()}
  </div>
</div>

<style>
  .exploration-workspace {
    display: grid;
    grid-template-columns: 1fr 360px;
    gap: 1rem;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem 1rem;
    min-height: 0;
  }

  .workspace-left {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    min-width: 0;
    overflow: auto;
  }

  .workspace-right {
    min-height: 0;
  }

  @media (max-width: 1024px) {
    .exploration-workspace {
      grid-template-columns: 1fr 300px;
    }
  }

  @media (max-width: 768px) {
    .exploration-workspace {
      grid-template-columns: 1fr;
    }
  }
</style>
