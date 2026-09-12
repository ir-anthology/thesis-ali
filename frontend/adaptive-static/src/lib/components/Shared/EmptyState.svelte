<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    icon,
    title,
    description,
    children
  }: {
    icon?: Snippet;
    title: string;
    description?: string;
    children?: Snippet;
  } = $props();
</script>

<div class="empty-state">
  {#if icon}
    <div class="empty-icon">{@render icon()}</div>
  {/if}
  <h2 class="empty-title">{title}</h2>
  {#if description}
    <p class="empty-description">{description}</p>
  {/if}
  {#if children}
    <div class="empty-actions">{@render children()}</div>
  {/if}
</div>

<style>
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    padding: 1rem;
  }

  .empty-icon {
    color: var(--accent);
    margin-bottom: 0.75rem;
    opacity: 0.8;
  }

  .empty-title {
    font-size: 1.0625rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.375rem;
    letter-spacing: -0.01em;
  }

  .empty-description {
    color: var(--text-secondary);
    max-width: 320px;
    font-size: 0.8125rem;
    line-height: 1.5;
  }

  .empty-actions {
    margin-top: 1.25rem;
    width: 100%;
    max-width: 320px;
  }

  @media (max-width: 640px) {
    .empty-state {
      padding: 0.75rem;
    }

    .empty-title {
      font-size: 1rem;
    }

    .empty-description {
      font-size: 0.75rem;
    }
  }
</style>
