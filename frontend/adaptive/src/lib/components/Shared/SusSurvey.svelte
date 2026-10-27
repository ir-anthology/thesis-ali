<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { getAnalyticsSessionId } from '$lib/analytics';

  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
  const NEXT_PROMPT_AFTER_KEY = 'ir-anthology-sus-next-prompt-after';
  const SUBMITTED_KEY = 'ir-anthology-sus-submitted';
  const PROMPT_AFTER_REPLIES = 5;

  const questions = [
    'I think that I would like to use this system frequently.',
    'I found the system unnecessarily complex.',
    'I thought the system was easy to use.',
    'I think that I would need the support of a technical person to be able to use this system.',
    'I found the various functions in this system were well integrated.',
    'I thought there was too much inconsistency in this system.',
    'I would imagine that most people would learn to use this system very quickly.',
    'I found the system very cumbersome to use.',
    'I felt very confident using the system.',
    'I needed to learn a lot of things before I could get going with this system.'
  ];

  const scaleLabels = [
    'Strongly disagree',
    'Disagree',
    'Neither agree nor disagree',
    'Agree',
    'Strongly agree'
  ];

  let {
    completedAssistantReplies
  }: {
    completedAssistantReplies: number;
  } = $props();

  let dialog: HTMLDialogElement;
  let triggerButton: HTMLButtonElement | null = null;
  let mounted = $state(false);
  let answers = $state<(number | null)[]>(Array(10).fill(null));
  let submitting = $state(false);
  let submitted = $state(false);
  let errorMessage = $state('');
  let answeredCount = $derived(answers.filter((answer) => answer !== null).length);
  let allAnswered = $derived(answeredCount === questions.length);

  function sessionStorageOrNull(): Storage | null {
    if (typeof window === 'undefined') return null;
    try {
      return window.sessionStorage;
    } catch {
      return null;
    }
  }

  function hasSessionFlag(key: string): boolean {
    try {
      return sessionStorageOrNull()?.getItem(key) === 'true';
    } catch {
      return false;
    }
  }

  function setSessionFlag(key: string): void {
    try {
      sessionStorageOrNull()?.setItem(key, 'true');
    } catch {
      // The survey remains usable if browser storage is unavailable.
    }
  }

  function getNextPromptAfter(): number {
    const storedValue = sessionStorageOrNull()?.getItem(NEXT_PROMPT_AFTER_KEY);
    if (storedValue === null || storedValue === undefined) return PROMPT_AFTER_REPLIES;
    const threshold = Number(storedValue);
    return Number.isFinite(threshold) && threshold >= 0 ? threshold : PROMPT_AFTER_REPLIES;
  }

  function deferSurvey(): void {
    try {
      sessionStorageOrNull()?.setItem(
        NEXT_PROMPT_AFTER_KEY,
        String(completedAssistantReplies + PROMPT_AFTER_REPLIES)
      );
    } catch {
      // The survey remains usable if browser storage is unavailable.
    }
  }

  onMount(() => {
    mounted = true;
    submitted = hasSessionFlag(SUBMITTED_KEY);
  });

  $effect(() => {
    if (
      mounted &&
      !submitted &&
      completedAssistantReplies >= getNextPromptAfter() &&
      !dialog?.open
    ) {
      openSurvey();
    }
  });

  function openSurvey(): void {
    errorMessage = '';
    if (!dialog?.open) dialog?.showModal();
  }

  function closeSurvey(): void {
    if (dialog?.open) dialog.close();
  }

  function handleDialogClose(): void {
    if (!submitted) deferSurvey();
    void tick().then(() => triggerButton?.focus());
  }

  function handleDialogClick(event: MouseEvent): void {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    const clickedBackdrop =
      event.clientX < bounds.left ||
      event.clientX > bounds.right ||
      event.clientY < bounds.top ||
      event.clientY > bounds.bottom;
    if (clickedBackdrop) closeSurvey();
  }

  async function submitSurvey(): Promise<void> {
    if (!allAnswered || submitting || submitted) return;

    submitting = true;
    errorMessage = '';
    try {
      const response = await fetch(`${API_BASE}/api/sus`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Id': getAnalyticsSessionId()
        },
        body: JSON.stringify({
          questionnaire: 'SUS',
          version: 'brooke-1996',
          answers
        })
      });

      if (!response.ok) throw new Error(`Survey submission failed (${response.status})`);

      submitted = true;
      setSessionFlag(SUBMITTED_KEY);
    } catch {
      errorMessage = 'We could not send your answers. Please try again.';
    } finally {
      submitting = false;
    }
  }
</script>

<button
  bind:this={triggerButton}
  class="survey-trigger"
  type="button"
  onclick={openSurvey}
  aria-haspopup="dialog"
>
  {submitted ? 'Usability survey submitted' : 'Rate usability'}
</button>

<dialog
  bind:this={dialog}
  class="survey-dialog"
  aria-labelledby="sus-title"
  aria-describedby="sus-description"
  onclick={handleDialogClick}
  onclose={handleDialogClose}
>
  {#if submitted}
    <section class="success-state" aria-live="polite">
      <div class="dialog-heading">
        <div>
          <p class="eyebrow">IR Anthology Chat</p>
          <h2 id="sus-title">Thank you for your feedback</h2>
        </div>
        <button class="icon-close" type="button" onclick={closeSurvey} aria-label="Close survey">×</button>
      </div>
      <p id="sus-description">Your usability survey has been submitted.</p>
      <div class="dialog-actions">
        <button class="primary-button" type="button" onclick={closeSurvey}>Close</button>
      </div>
    </section>
  {:else}
    <div class="dialog-heading">
      <div>
        <p class="eyebrow">IR Anthology Chat</p>
        <h2 id="sus-title">Help us understand how the demo feels to use</h2>
      </div>
      <button class="icon-close" type="button" onclick={closeSurvey} aria-label="Remind me later" title="Remind me later">×</button>
    </div>

    <p id="sus-description" class="intro">
      Please rate each statement based on your experience. Your answers are optional until you submit.
      When submitted, your ratings are sent with a temporary session ID, without your name or chat history.
      Choose “Remind me later” to see this again after five more completed assistant replies.
    </p>

    <div class="scale-key" aria-label="Answer choices">
      {#each scaleLabels as label, index (label)}
        <span><b>{index + 1}</b> {label}</span>
      {/each}
    </div>

    <div class="question-list">
      {#each questions as question, questionIndex (question)}
        <fieldset class="question">
          <legend><span class="question-number">{questionIndex + 1}.</span> {question}</legend>
          <div class="answer-options" role="radiogroup" aria-label={`Question ${questionIndex + 1}`}>
            {#each [1, 2, 3, 4, 5] as score (score)}
              <label class="answer-option" for={`sus-q${questionIndex + 1}-${score}`}>
                <input
                  id={`sus-q${questionIndex + 1}-${score}`}
                  type="radio"
                  name={`sus-q${questionIndex + 1}`}
                  value={score}
                  bind:group={answers[questionIndex]}
                  aria-label={`${score}: ${scaleLabels[score - 1]}`}
                />
                <span>{score}</span>
              </label>
            {/each}
          </div>
        </fieldset>
      {/each}
    </div>

    <p class="progress" aria-live="polite">Answered {answeredCount} of {questions.length}</p>
    {#if errorMessage}
      <p class="submission-error" role="alert">{errorMessage}</p>
    {/if}

    <div class="dialog-actions">
      <button class="secondary-button" type="button" onclick={closeSurvey}>Remind me later</button>
      <button
        class="primary-button"
        type="button"
        onclick={submitSurvey}
        disabled={!allAnswered || submitting}
      >
        {submitting ? 'Submitting…' : 'Submit answers'}
      </button>
    </div>
    <p class="attribution">System Usability Scale (SUS), based on Brooke (1996).</p>
  {/if}
</dialog>

<style>
  .survey-trigger,
  .secondary-button,
  .primary-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 0.375rem 0.75rem;
    background: white;
    color: #374151;
    font: inherit;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.15s ease, border-color 0.15s ease;
  }

  .survey-trigger:hover,
  .secondary-button:hover { background: #f9fafb; }
  .survey-trigger:focus-visible,
  .icon-close:focus-visible,
  .secondary-button:focus-visible,
  .primary-button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

  .survey-dialog {
    position: fixed;
    inset: 0;
    margin: auto;
    width: min(46rem, calc(100vw - 2rem));
    max-width: none;
    height: 750px;
    max-height: calc(100dvh - 1rem);
    padding: 1.25rem;
    overflow: auto;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--bg-elevated);
    color: var(--text-primary);
    box-shadow: 0 24px 64px rgba(15, 23, 42, 0.28);
  }

  .survey-dialog[open] { animation: survey-enter 0.16s ease-out; }
  .survey-dialog::backdrop { background: rgba(15, 23, 42, 0.52); }

  .dialog-heading {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
  }

  .eyebrow {
    margin-bottom: 0.25rem;
    color: var(--text-muted);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  h2 { max-width: 36rem; font-size: 1.25rem; line-height: 1.35; }
  .intro { margin-top: 0.75rem; color: var(--text-secondary); }

  .icon-close {
    display: grid;
    flex: 0 0 auto;
    width: 2rem;
    height: 2rem;
    place-items: center;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: white;
    color: var(--text-secondary);
    font-size: 1.4rem;
    line-height: 1;
    cursor: pointer;
  }

  .scale-key {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 0.5rem;
    margin: 0.75rem 0 0.15rem 45%;
    color: var(--text-muted);
    font-size: 0.65rem;
    line-height: 1.25;
    text-align: center;
  }

  .scale-key b {
    display: block;
    margin-bottom: 0.2rem;
    color: var(--text-primary);
    font-size: 0.75rem;
  }

  .question-list { border-top: 1px solid var(--border-light); }
  .question {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(15rem, 1fr);
    align-items: center;
    gap: 1rem;
    min-width: 0;
    padding: 0.4rem 0;
    border: 0;
    border-bottom: 1px solid var(--border-light);
  }

  .question legend { display: block; float: left; width: 100%; font-size: 0.875rem; line-height: 1.4; }
  .question-number { margin-right: 0.2rem; color: var(--text-muted); font-weight: 600; }

  .answer-options {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 0.35rem;
  }

  .answer-option {
    display: flex;
    min-width: 0;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    color: var(--text-secondary);
    font-size: 0.75rem;
    cursor: pointer;
  }

  .answer-option input { accent-color: var(--accent); }
  .answer-option input:focus-visible { outline-offset: 3px; }
  .answer-option span { color: var(--text-muted); }

  .progress { margin-top: 0.75rem; color: var(--text-secondary); font-size: 0.8125rem; }
  .submission-error { margin-top: 0.5rem; color: var(--error); }
  .dialog-actions { display: flex; justify-content: flex-end; gap: 0.625rem; margin-top: 0.75rem; }
  .primary-button { border-color: var(--accent); background: var(--accent); color: white; }
  .primary-button:hover:not(:disabled) { border-color: var(--accent-hover); background: var(--accent-hover); }
  .primary-button:disabled { opacity: 0.55; cursor: not-allowed; }
  .attribution { margin-top: 0.75rem; color: var(--text-muted); font-size: 0.7rem; text-align: right; }
  .success-state > p:not(.eyebrow) { margin-top: 0.75rem; color: var(--text-secondary); }

  @keyframes survey-enter {
    from { opacity: 0; transform: translateY(6px) scale(0.99); }
    to { opacity: 1; transform: translateY(0) scale(1); }
  }

  @media (max-width: 640px) {
    .survey-dialog { padding: 1rem; }
    .scale-key { margin-left: 0; font-size: 0.58rem; }
    .question { grid-template-columns: 1fr; gap: 0.55rem; padding: 0.75rem 0; }
    .answer-options { max-width: 22rem; margin-left: auto; }
    .dialog-actions { flex-direction: column-reverse; }
    .dialog-actions button { width: 100%; }
  }

  @media (prefers-reduced-motion: reduce) {
    .survey-dialog[open] { animation: none; }
  }
</style>
