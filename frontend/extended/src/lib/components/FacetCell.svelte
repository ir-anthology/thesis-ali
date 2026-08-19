<script lang="ts">
  import type { Facet } from '$lib/types/exploration';

  let {
    value,
    isTarget = false,
    facet,
    disabled = false,
    onActivate,
    onHoverStart,
    onHoverEnd
  }: {
    value: number | string;
    isTarget?: boolean;
    facet: Facet;
    disabled?: boolean;
    onActivate?: () => void;
    onHoverStart?: () => void;
    onHoverEnd?: () => void;
  } = $props();

  let isHovered = $state(false);

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (!isTarget && !disabled && onActivate) {
        onActivate();
      }
    }
  }

  function handleMouseEnter() {
    isHovered = true;
    if (!isTarget && !disabled && onHoverStart) {
      onHoverStart();
    }
  }

  function handleMouseLeave() {
    isHovered = false;
    if (!isTarget && !disabled && onHoverEnd) {
      onHoverEnd();
    }
  }

  function handleClick() {
    if (!isTarget && !disabled && onActivate) {
      onActivate();
    }
  }
</script>

<td
  class="facet-cell"
  class:is-target={isTarget}
  class:is-interactive={!isTarget && !disabled}
  class:is-hovered={isHovered}
  class:is-disabled={disabled}
  role={!isTarget && !disabled ? 'button' : undefined}
  tabindex={!isTarget && !disabled ? 0 : undefined}
  onclick={handleClick}
  onkeydown={handleKeydown}
  onmouseenter={handleMouseEnter}
  onmouseleave={handleMouseLeave}
  onfocus={handleMouseEnter}
  onblur={handleMouseLeave}
  aria-label={!isTarget && !disabled ? `Explore ${value} ${facet}s` : undefined}
>
  {value}
</td>

<style>
  .facet-cell {
    padding: 0.5rem 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border-light);
    font-size: 0.8125rem;
    color: var(--text-primary);
    white-space: nowrap;
    transition: background-color 0.1s ease;
  }

  .facet-cell.is-target {
    background-color: var(--target-accent-light);
    border-left: 3px solid var(--target-accent);
    font-weight: 600;
  }

  .facet-cell.is-interactive {
    cursor: pointer;
  }

  .facet-cell.is-interactive:hover,
  .facet-cell.is-interactive.is-hovered {
    background-color: var(--cell-hover);
  }

  .facet-cell.is-interactive:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: -2px;
  }

  .facet-cell.is-disabled {
    background-color: var(--cell-disabled-bg);
    color: var(--cell-disabled-text);
    cursor: not-allowed;
  }
</style>
