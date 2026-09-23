<script lang="ts">
  import { onMount } from 'svelte';
  import {
    dismissPrivacyNotice,
    isPrivacyNoticeDismissed,
    setAnalyticsEnabled
  } from '$lib/analytics';

  let visible = $state(false);

  onMount(() => {
    visible = !isPrivacyNoticeDismissed();
  });

  function choose(value: boolean): void {
    setAnalyticsEnabled(value);
    dismissPrivacyNotice();
    visible = false;
  }

  function openSettings(): void {
    visible = true;
  }
</script>

{#if visible}
  <aside class="privacy-notice" aria-label="Data collection notice">
    <div class="notice-copy">
      <strong>Help us improve IR Anthology Chat</strong>
      <p>
        We collect conversations and usage information to improve this service.
        Data is stored anonymously and you can opt out at any time.
      </p>
    </div>
    <div class="notice-actions">
      <button class="notice-button allow-button" onclick={() => choose(true)}>Allow data collection</button>
      <button class="notice-button" onclick={() => choose(false)}>Opt out</button>
    </div>
  </aside>
{:else}
  <button class="privacy-settings" onclick={openSettings} aria-label="Open data collection settings">
    Privacy settings
  </button>
{/if}

<style>
  .privacy-notice {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: center;
    padding: 0.75rem 1rem;
    border: 1px solid #b6d4fe;
    border-radius: 8px;
    background: #f0f7ff;
    color: var(--text-primary);
    font-size: 0.75rem;
  }

  .notice-copy { min-width: 0; }
  .notice-copy p { margin-top: 0.2rem; color: var(--text-secondary); }
  .notice-actions { display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0; }
  .notice-button, .privacy-settings {
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 0.3rem 0.55rem;
    background: var(--bg-primary);
    color: var(--text-primary);
    cursor: pointer;
    font: inherit;
  }
  .allow-button { background: var(--accent); border-color: var(--accent); color: white; }
  .allow-button:hover { background: var(--accent-hover); }
  .privacy-settings { align-self: flex-end; margin-top: 0.35rem; color: var(--text-secondary); }
  @media (max-width: 640px) {
    .privacy-notice { align-items: flex-start; flex-direction: column; }
    .notice-actions { width: 100%; justify-content: space-between; }
  }
</style>
