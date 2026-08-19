<script lang="ts">
  import type { Observation, FollowUpQuestion } from '$lib/types/exploration';
  import ObservationItem from './ObservationItem.svelte';
  import FollowUpButton from './FollowUpButton.svelte';

  let {
    observations,
    followUpQuestions,
    onFollowUp
  }: {
    observations: Observation[];
    followUpQuestions: FollowUpQuestion[];
    onFollowUp: (text: string) => void;
  } = $props();
</script>

<aside class="insights-panel">
  <div class="panel-header">
    <div class="header-badge">
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2a10 10 0 1 0 10 10 4 4 0 0 1-5-5 4 4 0 0 1-5-5"></path>
        <path d="M8.5 8.5v.01"></path>
        <path d="M16 15.5v.01"></path>
        <path d="M12 12v.01"></path>
        <path d="M11 17v.01"></path>
        <path d="M7 14.5v.01"></path>
      </svg>
      AI Observations
    </div>
  </div>

  {#if observations.length === 0}
    <div class="empty-observations">
      <p>Observations will appear here after a query.</p>
    </div>
  {:else}
    <div class="observations-list">
      {#each observations as observation (observation.id)}
        <ObservationItem text={observation.text} />
      {/each}
    </div>
  {/if}

  <div class="panel-divider"></div>

  <div class="section-header">
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="m21 15-3-3v-3.36c0-.53-.4-.96-.9-.96L12 7.76"></path>
      <path d="M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z"></path>
      <path d="M8 12h.01"></path>
      <path d="M12 12h.01"></path>
      <path d="M16 12h.01"></path>
    </svg>
    <span>Suggested Questions</span>
  </div>

  {#if followUpQuestions.length === 0}
    <div class="empty-questions">
      <p>Follow-up questions will appear here.</p>
    </div>
  {:else}
    <div class="questions-list">
      {#each followUpQuestions as question (question.id)}
        <FollowUpButton text={question.text} onClick={() => onFollowUp(question.text)} />
      {/each}
    </div>
  {/if}
</aside>

<style>
  .insights-panel {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    background-color: var(--observation-bg);
    border: 1px solid var(--observation-border);
    border-radius: 8px;
    padding: 1rem;
    height: fit-content;
  }

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .header-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.625rem;
    background-color: var(--accent);
    color: white;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .header-badge svg {
    opacity: 0.8;
  }

  .observations-list {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .panel-divider {
    height: 1px;
    background-color: var(--observation-border);
    margin: 0.25rem 0;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--text-secondary);
  }

  .section-header svg {
    color: var(--accent);
  }

  .questions-list {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
  }

  .empty-observations,
  .empty-questions {
    padding: 1rem 0;
    text-align: center;
  }

  .empty-observations p,
  .empty-questions p {
    font-size: 0.8125rem;
    color: var(--text-muted);
  }
</style>
