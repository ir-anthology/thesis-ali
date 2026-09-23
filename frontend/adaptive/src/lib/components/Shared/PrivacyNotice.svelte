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

</script>

{#if visible}
  <div class="privacy-backdrop">
    <div class="privacy-notice" role="dialog" aria-modal="true" aria-labelledby="privacy-title">
      <div class="notice-copy">
        <strong id="privacy-title">Help us improve IR Anthology Chat</strong>
        <p>
          We collect conversations and usage information to improve this service.
          Data is stored anonymously and you can opt out at any time.
        </p>
      </div>
      <div class="notice-actions">
        <button class="notice-button allow-button" onclick={() => choose(true)}>Allow data collection</button>
        <button class="notice-button" onclick={() => choose(false)}>Opt out</button>
      </div>
    </div>
  </div>
{:else}
  <button class="privacy-settings-button" onclick={() => (visible = true)}>
    Privacy settings
  </button>
{/if}

<style>
  .privacy-backdrop {
    position: fixed;
    inset: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.25rem;
    background: rgba(15, 23, 42, 0.42);
  }

  .privacy-notice {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    width: min(100%, 34rem);
    padding: 1.5rem;
    border: 1px solid #b6d4fe;
    border-radius: 8px;
    background: #f0f7ff;
    color: var(--text-primary);
    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.22);
    font-size: 0.95rem;
  }

  .notice-copy { min-width: 0; }
  .notice-copy strong { display: block; font-size: 1.05rem; }
  .notice-copy p { margin-top: 0.5rem; color: var(--text-secondary); line-height: 1.5; }
  .notice-actions { display: flex; justify-content: flex-end; align-items: center; gap: 0.75rem; flex-shrink: 0; }
  .notice-button {
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 0.45rem 0.7rem;
    background: var(--bg-primary);
    color: var(--text-primary);
    cursor: pointer;
    font: inherit;
  }
  .allow-button { background: var(--accent); border-color: var(--accent); color: white; }
  .allow-button:hover { background: var(--accent-hover); }
  .privacy-settings-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
    font-weight: 500;
    font-family: inherit;
    background-color: white;
    color: #374151;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    border: 1px solid #d1d5db;
    cursor: pointer;
    transition: background-color 0.15s ease;
  }
  .privacy-settings-button:hover { background-color: #f9fafb; }
  .privacy-settings-button:focus-visible {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
  }
  @media (max-width: 640px) {
    .privacy-backdrop { align-items: flex-start; padding-top: 5rem; }
    .notice-actions { width: 100%; justify-content: stretch; flex-direction: column; }
    .notice-button { width: 100%; }
  }
</style>
