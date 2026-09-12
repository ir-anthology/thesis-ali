<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    variant = 'default',
    children
  }: {
    variant?: 'default' | 'accent' | 'success' | 'warning' | 'error';
    children: Snippet;
  } = $props();
</script>

<span class="badge {variant}">
  {@render children()}
</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    padding: 0.125rem 0.5rem;
    font-size: 0.6875rem;
    font-weight: 500;
    border-radius: 9999px;
    line-height: 1.4;
    white-space: nowrap;
  }

  .default {
    background-color: var(--bg-tertiary);
    color: var(--text-secondary);
  }

  .accent {
    background-color: var(--accent-light);
    color: var(--accent);
  }

  .success {
    background-color: #d1e7dd;
    color: var(--success);
  }

  .warning {
    background-color: #fff3cd;
    color: #664d03;
  }

  .error {
    background-color: #f8d7da;
    color: var(--error);
  }
</style>
