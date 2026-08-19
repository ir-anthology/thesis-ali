<script lang="ts">
  let {
    text = '',
    visible = false,
    position = { x: 0, y: 0 }
  }: {
    text?: string;
    visible?: boolean;
    position?: { x: number; y: number };
  } = $props();
</script>

{#if visible && text}
  <div
    class="tooltip"
    class:visible
    role="tooltip"
    style="left: {position.x}px; top: {position.y}px;"
  >
    <div class="tooltip-arrow"></div>
    {text}
  </div>
{/if}

<style>
  .tooltip {
    position: fixed;
    z-index: 50;
    max-width: 280px;
    padding: 0.5rem 0.75rem;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
    font-size: 0.8125rem;
    color: var(--text-primary);
    line-height: 1.4;
    opacity: 0;
    transform: translateY(4px);
    transition: opacity 0.15s ease, transform 0.15s ease;
    pointer-events: none;
  }

  .tooltip.visible {
    opacity: 1;
    transform: translateY(0);
  }

  .tooltip-arrow {
    position: absolute;
    left: 12px;
    top: -5px;
    width: 8px;
    height: 8px;
    background: var(--bg-elevated);
    border-top: 1px solid var(--border);
    border-left: 1px solid var(--border);
    transform: rotate(45deg);
  }
</style>
