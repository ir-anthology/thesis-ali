<script lang="ts">
  let {
    label,
    onRemove
  }: {
    label: string;
    onRemove: () => void;
  } = $props();
</script>

<span class="pill">
  <span class="pill-label">{label}</span>
  <button class="pill-remove" onclick={onRemove} aria-label="Remove filter {label}">
    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <line x1="18" y1="6" x2="6" y2="18"></line>
      <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
  </button>
</span>

<style>
  .pill {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.1875rem 0.375rem 0.1875rem 0.625rem;
    background-color: var(--accent-light);
    color: var(--accent);
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .pill-label {
    line-height: 1.4;
  }

  .pill-remove {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    border: none;
    background: transparent;
    color: var(--accent);
    cursor: pointer;
    border-radius: 50%;
    transition: background-color 0.15s ease;
    padding: 0;
  }

  .pill-remove:hover {
    background-color: var(--accent);
    color: white;
  }
</style>
