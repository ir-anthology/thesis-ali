<script lang="ts">
  import type { ConversationTurn } from '$lib/types/exploration';

  let {
    message,
    disabled = false,
    onEdit
  }: {
    message: ConversationTurn;
    disabled?: boolean;
    onEdit?: (turnId: string, content: string) => void;
  } = $props();

  let editing = $state(false);
  let editValue = $state('');
  let textarea: HTMLTextAreaElement | undefined = $state();

  function formatTime(date: Date): string {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function startEditing(): void {
    if (disabled || !onEdit) return;
    editValue = message.content;
    editing = true;
  }

  function cancelEditing(): void {
    editing = false;
    editValue = '';
  }

  function saveEdit(): void {
    const nextContent = editValue.trim();
    if (!nextContent || nextContent === message.content || disabled || !onEdit) return;
    onEdit(message.id, nextContent);
    editing = false;
    editValue = '';
  }

  function handleKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      saveEdit();
      return;
    }

    if (event.key === 'Escape') {
      event.preventDefault();
      cancelEditing();
    }
  }

  function autoResize(): void {
    if (!textarea) return;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 160) + 'px';
  }

  $effect(() => {
    if (editing && textarea) {
      textarea.focus();
      textarea.setSelectionRange(textarea.value.length, textarea.value.length);
      autoResize();
    }
  });

  $effect(() => {
    editValue;
    autoResize();
  });
</script>

<div class="message user">
  <div class="avatar">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
      <circle cx="12" cy="7" r="4"></circle>
    </svg>
  </div>
  <div class="content">
    <div class="message-header">
      <span class="role">You</span>
      <span class="time">{formatTime(message.timestamp)}</span>
    </div>
    <div class="message-body">
      {#if editing}
        <textarea
          bind:this={textarea}
          bind:value={editValue}
          onkeydown={handleKeydown}
          rows="1"
          aria-label="Edit message"
          disabled={disabled}
        ></textarea>
        <div class="edit-actions">
          <button class="cancel-btn" type="button" onclick={cancelEditing} disabled={disabled}>
            Cancel
          </button>
          <button
            class="save-btn"
            type="button"
            onclick={saveEdit}
            disabled={!editValue.trim() || editValue.trim() === message.content || disabled}
          >
            Save
          </button>
        </div>
      {:else}
        <p>{message.content}</p>
      {/if}
    </div>
  </div>
  {#if onEdit && !editing && !disabled}
    <button
      class="edit-btn"
      type="button"
      onclick={startEditing}
      disabled={disabled}
      title="Edit message"
      aria-label="Edit message"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 20h9"></path>
        <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"></path>
      </svg>
    </button>
  {/if}
</div>

<style>
  .message {
    display: flex;
    position: relative;
    gap: 0.625rem;
    padding: 0.75rem 1rem;
    animation: fadeIn 0.2s ease-out;
    flex-direction: row-reverse;
  }

  .avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    background-color: var(--accent);
    color: white;
  }

  .content {
    position: relative;
    flex: 0 1 auto;
    min-width: 0;
    width: fit-content;
    max-width: calc(100% - 28px - 0.625rem);
    padding: 0.625rem 0.875rem;
    background-color: var(--user-bubble);
    border-radius: 12px 12px 2px 12px;
  }

  .message-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
  }

  .role {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  .time {
    font-size: 0.6875rem;
    color: var(--text-muted);
  }

  .message-body {
    color: var(--accent);
    line-height: 1.5;
    font-size: 0.8125rem;
  }

  .message-body p {
    margin: 0;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    padding-right: 1.375rem;
  }

  .edit-btn {
    position: absolute;
    right: calc(28px + 0.625rem - 0.25rem);
    bottom: -0.875rem;
    width: 28px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--border);
    border-radius: 50%;
    background-color: var(--bg-primary);
    color: var(--text-secondary);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
    cursor: pointer;
    opacity: 0;
    pointer-events: none;
    z-index: 1;
    transition: opacity 0.15s ease, color 0.15s ease, background-color 0.15s ease;
  }

  .message:hover .edit-btn,
  .message:focus-within .edit-btn {
    opacity: 1;
    pointer-events: auto;
  }

  .edit-btn:hover:not(:disabled) {
    color: var(--accent);
    background-color: var(--bg-secondary);
  }

  .edit-btn:disabled {
    cursor: not-allowed;
    opacity: 0;
  }

  textarea {
    width: min(34rem, 64vw);
    min-width: min(24rem, 64vw);
    max-height: 160px;
    padding: 0.5rem 0.625rem;
    border: 1px solid var(--border);
    border-radius: 8px;
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font: inherit;
    line-height: 1.5;
    resize: none;
    outline: none;
  }

  textarea:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px color-mix(in srgb, var(--accent) 18%, transparent);
  }

  textarea:disabled {
    opacity: 0.5;
  }

  .edit-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }

  .cancel-btn,
  .save-btn {
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.3125rem 0.625rem;
    font: inherit;
    font-size: 0.75rem;
    font-weight: 500;
    cursor: pointer;
  }

  .cancel-btn {
    background-color: var(--bg-primary);
    color: var(--text-secondary);
  }

  .save-btn {
    background-color: var(--accent);
    border-color: var(--accent);
    color: white;
  }

  .cancel-btn:hover:not(:disabled) {
    background-color: var(--bg-secondary);
  }

  .save-btn:hover:not(:disabled) {
    background-color: var(--accent-hover);
  }

  .cancel-btn:disabled,
  .save-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(6px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @media (max-width: 640px) {
    .message {
      padding: 0.625rem 0.75rem;
    }
  }
</style>
