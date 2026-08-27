# Development Plan: Adaptive Conversational Knowledge Graph Explorer

## Project Overview

Build a SvelteKit frontend in `frontend/adaptive/` that implements an LLM-assisted exploratory search interface for scholarly knowledge graphs. The UI adapts dynamically to conversation state — no fixed three-panel layout. Uses mock data for all rendering.

**Tech Stack:** Svelte 5 (runes), SvelteKit, Tailwind CSS v4, TypeScript

---

## Phase 0: Project Scaffolding

**Goal:** Set up SvelteKit project with Tailwind CSS and design tokens.

### Steps:

1. **Initialize SvelteKit project** in `frontend/adaptive/`

   ```bash
   npx sv create frontend/adaptive --template minimal --types ts
   ```

   Select: Svelte 5, TypeScript, Tailwind CSS

2. **Create `src/app.css`** with design tokens (custom properties):

   ```css
   @import 'tailwindcss';

   :root {
     /* Surfaces */
     --bg-primary: #ffffff;
     --bg-secondary: #f8f9fa;
     --bg-tertiary: #e9ecef;
     --bg-elevated: #ffffff;

      /* Text */
      --text-primary: #212529;
      --text-secondary: #6c757d;
      --text-muted: #6c757d; /* Changed from #adb5bd for WCAG AA (≥4.5:1) */

     /* Accent */
     --accent: #0d6efd;
     --accent-hover: #0b5ed7;
     --accent-light: #e7f1ff;

     /* Message bubbles */
     --user-bubble: #e7f1ff;
     --assistant-bubble: #f8f9fa;

     /* AI interpretation */
     --ai-interpretation-bg: #f0f7ff;
     --ai-interpretation-border: #b6d4fe;

     /* Code */
     --code-bg: #f6f8fa;
     --code-border: #e9ecef;

     /* Borders */
     --border: #dee2e6;
     --border-light: #e9ecef;

     /* Status */
     --error: #dc3545;
     --success: #198754;
     --warning: #ffc107;
   }
   ```

   Also include:
   - Box-sizing reset
   - Font family: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
   - Font size: `0.875rem` base
   - Custom scrollbar styles (6px width, subtle thumb)
   - `fadeIn` animation for new messages
   - `spin` animation for loading spinner
   - `pulse` animation for loading states
   - `:focus-visible` outline (2px accent, 2px offset)
   - `.sr-only` utility class

3. **Create `src/app.html`** (standard SvelteKit shell):

   ```html
   <!doctype html>
   <html lang="en">
     <head>
       <meta charset="utf-8" />
       <link rel="icon" href="%sveltekit.assets%/favicon.svg" />
       <meta name="viewport" content="width=device-width, initial-scale=1" />
       %sveltekit.head%
     </head>
     <body data-sveltekit-preload-data="hover">
       <div style="display: contents">%sveltekit.body%</div>
     </body>
   </html>
   ```

4. **Create layout** `src/routes/+layout.svelte`:

   ```svelte
   <script>
     import '../app.css';
     let { children } = $props();
   </script>

   {@render children()}
   ```

---

## Phase 1: Data Model & Mock Data

**Goal:** Define TypeScript interfaces and mock data that represent the full exploration state.

### Files to create:

### 1. `src/lib/types/exploration.ts` — Core type definitions

```typescript
export type Facet = 'author' | 'venue' | 'year' | 'publication';
export type ResultType = 'facet_table' | 'entity_list' | 'comparison' | 'timeline' | 'summary';
export type SortDirection = 'asc' | 'desc';
export type MessageRole = 'user' | 'assistant';
export type ResponseStatus = 'answerable' | 'unsupported' | 'error';

export interface ConversationTurn {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  loading?: boolean;
  error?: boolean;
}

export interface SortState {
  field: string;
  direction: SortDirection;
}

export interface ResultColumn {
  key: string;
  label: string;
  type: 'text' | 'number' | 'badge' | 'link';
  sortable?: boolean;
}

export interface ResultRow {
  [key: string]: string | number;
}

export interface ResultState {
  type: ResultType;
  columns: ResultColumn[];
  rows: ResultRow[];
  title?: string;
}

export interface Observation {
  id: string;
  text: string;
  source: 'llm';
}

export interface FollowUpQuestion {
  id: string;
  text: string;
}

export interface Entity {
  id: string;
  name: string;
  type: Facet;
  facets: Record<string, string | number>;
}

export interface ExplorationContext {
  targetFacet: Facet | null;
  sorting: SortState | null;
  selectedEntities: Entity[];
}

export interface InterpretationState {
  observations: Observation[];
  suggestions: FollowUpQuestion[];
}

export interface ExplorationState {
  conversation: ConversationTurn[];
  context: ExplorationContext;
  result: ResultState | null;
  interpretation: InterpretationState;
  loading: boolean;
  error: string | null;
  activeView: ResultType | null;
}

export interface ExplorationResponse {
  status: ResponseStatus;
  conversation: ConversationTurn[];
  exploration: {
    targetFacet: Facet | null;
    sort: SortState | null;
  };
  result: ResultState;
  interpretation: InterpretationState;
}
```

### 2. `src/lib/data/mock-responses.ts` — Mock data for scenarios

Create mock responses for each of these conversation scenarios:

**Scenario 1: "Who are the most prolific authors in exploratory search?"**

```typescript
{
  status: 'answerable',
  result: {
    type: 'facet_table',
    title: 'Most Prolific Authors in Exploratory Search',
    columns: [
      { key: 'author', label: 'Author', type: 'text', sortable: true },
      { key: 'publications', label: 'Publications', type: 'number', sortable: true },
      { key: 'venues', label: 'Venues', type: 'number', sortable: true },
      { key: 'years', label: 'Years', type: 'text' }
    ],
    rows: [
      { author: 'Marti A. Hearst', publications: 42, venues: 12, years: '1995–2024' },
      { author: 'Ryen W. White', publications: 38, venues: 10, years: '2003–2024' },
      { author: 'Gary Marchionini', publications: 31, venues: 9, years: '1997–2023' },
      { author: 'Daniel M. Russell', publications: 27, venues: 8, years: '2000–2022' },
      { author: 'Andrei Z. Broder', publications: 24, venues: 7, years: '1998–2021' }
    ]
  },
  interpretation: {
    observations: [
      {
        id: 'obs-1',
        text: 'Marti A. Hearst leads with 42 publications spanning nearly three decades, indicating sustained research activity in exploratory search.',
        source: 'llm'
      }
    ],
    suggestions: [
      { id: 'sug-1', text: 'Only consider the last five years' },
      { id: 'sug-2', text: 'Which venues do these authors publish in?' },
      { id: 'sug-3', text: 'Show me how this changed over time' }
    ]
  }
}
```

**Scenario 2: "Only consider the last five years"** — Same structure, filtered rows (2020–2025), different data, filter bar shows `[Year: 2020–2025 ×]`

**Scenario 3: "Which venues do these authors publish in?"** — Pivot to venue facet table

```typescript
{
  result: {
    type: 'facet_table',
    title: 'Venues for Top Authors in Exploratory Search',
    columns: [
      { key: 'venue', label: 'Venue', type: 'text', sortable: true },
      { key: 'publications', label: 'Publications', type: 'number', sortable: true },
      { key: 'authors', label: 'Authors', type: 'number', sortable: true },
      { key: 'years', label: 'Years', type: 'text' }
    ],
    rows: [
      { venue: 'SIGIR', publications: 18, authors: 5, years: '2020–2025' },
      { venue: 'CHIIR', publications: 9, authors: 4, years: '2021–2025' },
      { venue: 'CHI', publications: 7, authors: 3, years: '2020–2024' },
      { venue: 'UIST', publications: 5, authors: 2, years: '2020–2023' },
      { venue: 'JASIST', publications: 4, authors: 3, years: '2020–2024' }
    ]
  },
  interpretation: {
    observations: [
      {
        id: 'obs-3',
        text: 'SIGIR dominates as the primary venue, accounting for 18 publications across all five authors.',
        source: 'llm'
      }
    ],
    suggestions: [
      { id: 'sug-7', text: 'Show me how this changed over time' },
      { id: 'sug-8', text: 'Compare SIGIR and CHIIR' },
      { id: 'sug-9', text: 'Why is SIGIR prominent?' }
    ]
  }
}
```

**Scenario 4: "Show me how this changed over time"** — Timeline view

```typescript
{
  result: {
    type: 'timeline',
    title: 'Publication Activity Over Time',
    columns: [
      { key: 'year', label: 'Year', type: 'text' },
      { key: 'SIGIR', label: 'SIGIR', type: 'number' },
      { key: 'CHIIR', label: 'CHIIR', type: 'number' },
      { key: 'CHI', label: 'CHI', type: 'number' }
    ],
    rows: [
      { year: '2020', SIGIR: 12, CHIIR: 3, CHI: 2 },
      { year: '2021', SIGIR: 14, CHIIR: 4, CHI: 2 },
      { year: '2022', SIGIR: 15, CHIIR: 5, CHI: 1 },
      { year: '2023', SIGIR: 16, CHIIR: 6, CHI: 3 },
      { year: '2024', SIGIR: 18, CHIIR: 7, CHI: 2 },
      { year: '2025', SIGIR: 19, CHIIR: 8, CHI: 2 }
    ]
  },
  interpretation: {
    observations: [
      {
        id: 'obs-4',
        text: 'Publication activity at SIGIR shows a steady upward trend, growing from 12 to 19 publications over the period. CHIIR also shows consistent growth.',
        source: 'llm'
      }
    ],
    suggestions: [
      { id: 'sug-10', text: 'Compare SIGIR and CHIIR' },
      { id: 'sug-11', text: 'Which authors contributed most to this growth?' },
      { id: 'sug-12', text: 'Go back to all authors' }
    ]
  }
}
```

**Scenario 5: "Compare SIGIR and CHIIR"** — Comparison view

```typescript
{
  result: {
    type: 'comparison',
    title: 'SIGIR vs CHIIR',
    columns: [
      { key: 'metric', label: 'Metric', type: 'text' },
      { key: 'SIGIR', label: 'SIGIR', type: 'text' },
      { key: 'CHIIR', label: 'CHIIR', type: 'text' }
    ],
    rows: [
      { metric: 'Total Publications', SIGIR: '18', CHIIR: '9' },
      { metric: 'Authors', SIGIR: '5', CHIIR: '4' },
      { metric: 'Years Active', SIGIR: '2020–2025', CHIIR: '2021–2025' },
      { metric: 'Avg Publications/Year', SIGIR: '3.0', CHIIR: '1.8' },
      { metric: 'Growth Trend', SIGIR: 'Increasing', CHIIR: 'Stable' }
    ]
  },
  interpretation: {
    observations: [
      {
        id: 'obs-5',
        text: 'SIGIR has twice the publication volume of CHIIR and shows stronger growth. However, CHIIR has been steadily gaining relevance since its inception.',
        source: 'llm'
      }
    ],
    suggestions: [
      { id: 'sug-13', text: 'Why is SIGIR prominent?' },
      { id: 'sug-14', text: 'Which authors publish in both venues?' },
      { id: 'sug-15', text: 'Show publication trends for all venues' }
    ]
  }
}
```

**Scenario 6: "Why is SIGIR prominent?"** — Observation-focused response

```typescript
{
  result: {
    type: 'summary',
    title: 'Why SIGIR Is Prominent',
    columns: [],
    rows: []
  },
  interpretation: {
    observations: [
      {
        id: 'obs-6a',
        text: 'SIGIR (ACM Special Interest Group on Information Retrieval) is the premier venue for information retrieval research. It accounts for the highest publication count in the current result set.',
        source: 'llm'
      },
      {
        id: 'obs-6b',
        text: 'The venue has been active since the 1970s and consistently attracts top researchers in search, retrieval, and exploratory search specifically.',
        source: 'llm'
      },
      {
        id: 'obs-6c',
        text: 'In the current filtered context (top authors, last 5 years), SIGIR represents 38% of all publications.',
        source: 'llm'
      }
    ],
    suggestions: [
      { id: 'sug-16', text: 'Compare SIGIR and CHIIR' },
      { id: 'sug-17', text: 'Which authors publish most at SIGIR?' },
      { id: 'sug-18', text: 'Show all venues' }
    ]
  }
}
```

**Scenario 7: Unsupported question** — Error with alternatives

```typescript
{
  status: 'unsupported',
  result: {
    type: 'summary',
    title: 'Unsupported Query',
    columns: [],
    rows: []
  },
  interpretation: {
    observations: [
      {
        id: 'obs-7',
        text: 'I cannot answer that question using the current scholarly data and query capabilities. However, I can help you explore:',
        source: 'llm'
      }
    ],
    suggestions: [
      { id: 'sug-19', text: 'Which authors published in this venue?' },
      { id: 'sug-20', text: 'How did publication activity change over time?' },
      { id: 'sug-21', text: 'Show me the most cited papers' }
    ]
  }
}
```

### 3. `src/lib/data/mock-entities.ts` — Sample entity data

```typescript
export const mockAuthors = [
  { id: 'a1', name: 'Marti A. Hearst', type: 'author' as const, facets: { publications: 42, venues: 12, years: '1995–2024' } },
  { id: 'a2', name: 'Ryen W. White', type: 'author' as const, facets: { publications: 38, venues: 10, years: '2003–2024' } },
  { id: 'a3', name: 'Gary Marchionini', type: 'author' as const, facets: { publications: 31, venues: 9, years: '1997–2023' } },
  { id: 'a4', name: 'Daniel M. Russell', type: 'author' as const, facets: { publications: 27, venues: 8, years: '2000–2022' } },
  { id: 'a5', name: 'Andrei Z. Broder', type: 'author' as const, facets: { publications: 24, venues: 7, years: '1998–2021' } }
];

export const mockVenues = [
  { id: 'v1', name: 'SIGIR', type: 'venue' as const, facets: { publications: 88, years: '1971–2025' } },
  { id: 'v2', name: 'CHIIR', type: 'venue' as const, facets: { publications: 32, years: '2016–2025' } },
  { id: 'v3', name: 'CHI', type: 'venue' as const, facets: { publications: 25, years: '1982–2025' } },
  { id: 'v4', name: 'UIST', type: 'venue' as const, facets: { publications: 18, years: '1988–2025' } },
  { id: 'v5', name: 'JASIST', type: 'venue' as const, facets: { publications: 15, years: '1950–2025' } }
];

export const mockPublications = [
  { id: 'p1', title: 'User Interfaces and Support for Exploratory Search', type: 'publication' as const, facets: { author: 'Marti A. Hearst', venue: 'SIGIR', year: 2023 } },
  { id: 'p2', title: 'Search Interaction Patterns in Exploratory Tasks', type: 'publication' as const, facets: { author: 'Ryen W. White', venue: 'CHIIR', year: 2022 } },
  { id: 'p3', title: 'Faceted Search for Digital Libraries', type: 'publication' as const, facets: { author: 'Gary Marchionini', venue: 'JASIST', year: 2021 } }
];
```

---

## Phase 2: State Management Store

**Goal:** Create a reactive exploration store using Svelte 5 runes.

### File: `src/lib/stores/exploration.svelte.ts`

The store manages the entire exploration state using `$state`:

```typescript
import type {
  ConversationTurn,
  Facet,
  SortState,
  ResultState,
  Observation,
  FollowUpQuestion,
  Entity,
  ExplorationState
} from '$lib/types/exploration';
import { mockResponses } from '$lib/data/mock-responses';

function createExplorationStore() {
  // State
  let conversation = $state<ConversationTurn[]>([]);
  let targetFacet = $state<Facet | null>(null);
  let sorting = $state<SortState | null>(null);
  let result = $state<ResultState | null>(null);
  let observations = $state<Observation[]>([]);
  let suggestions = $state<FollowUpQuestion[]>([]);
  let selectedEntities = $state<Entity[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);

  let resultsByTurn = $state<Map<string, ResultState>>(new Map());
  let observationsByTurn = $state<Map<string, Observation[]>>(new Map());
  let suggestionsByTurn = $state<Map<string, FollowUpQuestion[]>>(new Map());

  // Helper
  function generateId(): string {
    return crypto.randomUUID();
  }

  // Match user message to mock response
  function findMockResponse(message: string): ExplorationResponse | null {
    // Simple keyword matching for mock scenarios
    const lower = message.toLowerCase();
    if (lower.includes('prolific') || lower.includes('most authors')) return mockResponses['prolific-authors'];
    if (lower.includes('last five') || lower.includes('last 5')) return mockResponses['filtered-years'];
    if (lower.includes('venue') || lower.includes('publish in')) return mockResponses['venues'];
    if (lower.includes('changed over time') || lower.includes('how has')) return mockResponses['timeline'];
    if (lower.includes('compare')) return mockResponses['comparison'];
    if (lower.includes('why') && lower.includes('sigir')) return mockResponses['why-sigir'];
    return mockResponses['unsupported'];
  }

  // Send message
  async function sendMessage(content: string): Promise<void> {
    if (!content.trim() || loading) return;

    const userTurn: ConversationTurn = {
      id: generateId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    };
    conversation = [...conversation, userTurn];

    const assistantTurn: ConversationTurn = {
      id: generateId(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      loading: true
    };
    conversation = [...conversation, assistantTurn];
    loading = true;
    error = null;

    // Simulate LLM delay
    await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 700));

    const response = findMockResponse(content);

    if (response) {
      conversation = conversation.map(t =>
        t.id === assistantTurn.id
          ? { ...t, content: response.result.title || 'Here are the results:', loading: false }
          : t
      );

      resultsByTurn = new Map(resultsByTurn).set(assistantTurn.id, response.result);
      observationsByTurn = new Map(observationsByTurn).set(assistantTurn.id, response.interpretation.observations);
      suggestionsByTurn = new Map(suggestionsByTurn).set(assistantTurn.id, response.interpretation.suggestions);

      result = response.result;
      observations = response.interpretation.observations;
      suggestions = response.interpretation.suggestions;
      if (response.exploration.targetFacet) targetFacet = response.exploration.targetFacet;
      if (response.exploration.sort) sorting = response.exploration.sort;
    } else {
      conversation = conversation.map(t =>
        t.id === assistantTurn.id
          ? { ...t, content: 'Sorry, I encountered an error. Please try again.', loading: false, error: true }
          : t
      );
      error = 'Failed to get response';
    }

    loading = false;
  }

  // Sorting
  function setSorting(sort: SortState): void {
    sorting = sort;
  }

  // Target facet
  function setTargetFacet(facet: Facet): void {
    targetFacet = facet;
  }

  // Entity selection
  function selectEntity(entity: Entity): void {
    if (!selectedEntities.find(e => e.id === entity.id)) {
      selectedEntities = [...selectedEntities, entity];
    }
  }

  function clearSelection(): void {
    selectedEntities = [];
  }

  // Suggestions
  function selectSuggestion(suggestion: FollowUpQuestion): void {
    sendMessage(suggestion.text);
  }

  // Retry
  function retry(): void {
    const lastUserTurn = [...conversation].reverse().find(t => t.role === 'user');
    if (lastUserTurn) {
      // Remove last assistant turn
      conversation = conversation.filter(t => !t.loading && !(t.role === 'assistant' && t.error));
      sendMessage(lastUserTurn.content);
    }
  }

  // Clear
  function clearExploration(): void {
    conversation = [];
    targetFacet = null;
    sorting = null;
    result = null;
    observations = [];
    suggestions = [];
    selectedEntities = [];
    loading = false;
    error = null;
    resultsByTurn = new Map();
    observationsByTurn = new Map();
    suggestionsByTurn = new Map();
    clearSessionStorage();
  }

  function saveState(): void {
    saveToSessionStorage({
      conversation,
      targetFacet,
      sorting,
      result,
      observations,
      suggestions,
      resultsByTurn: Object.fromEntries(resultsByTurn),
      observationsByTurn: Object.fromEntries(observationsByTurn),
      suggestionsByTurn: Object.fromEntries(suggestionsByTurn)
    });
  }

  function loadState(): boolean {
    const saved = loadFromSessionStorage();
    if (!saved) return false;

    conversation = saved.conversation;
    targetFacet = saved.targetFacet;
    sorting = saved.sorting;
    result = saved.result;
    observations = saved.observations;
    suggestions = saved.suggestions;
    resultsByTurn = new Map(Object.entries(saved.resultsByTurn || {}));
    observationsByTurn = new Map(Object.entries(saved.observationsByTurn || {}));
    suggestionsByTurn = new Map(Object.entries(saved.suggestionsByTurn || {}));
    loading = false;
    error = null;

    return true;
  }

  return {
    get conversation() { return conversation; },
    get targetFacet() { return targetFacet; },
    get sorting() { return sorting; },
    get result() { return result; },
    get observations() { return observations; },
    get suggestions() { return suggestions; },
    get selectedEntities() { return selectedEntities; },
    get loading() { return loading; },
    get error() { return error; },
    get resultsByTurn() { return resultsByTurn; },
    get observationsByTurn() { return observationsByTurn; },
    get suggestionsByTurn() { return suggestionsByTurn; },
    sendMessage,
    setSorting,
    setTargetFacet,
    selectEntity,
    clearSelection,
    selectSuggestion,
    retry,
    clearExploration,
    saveState,
    loadState
  };
}

export const exploration = createExplorationStore();
```

---

## Phase 3: Shared Components

**Goal:** Build reusable UI primitives following the design system.

### Components:

### `src/lib/components/Shared/Badge.svelte`

Small metadata badge with semantic styling.

```svelte
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
```

### `src/lib/components/Shared/Pill.svelte`

Removable filter pill.

```svelte
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
```

### `src/lib/components/Shared/Spinner.svelte`

```svelte
<script lang="ts">
  let { size = 16 }: { size?: number } = $props();
</script>

<div class="spinner" style="width: {size}px; height: {size}px;" role="status" aria-label="Loading">
  <span class="sr-only">Loading...</span>
</div>

<style>
  .spinner {
    border: 2px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
  }
</style>
```

### `src/lib/components/Shared/EmptyState.svelte`

```svelte
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
    padding: 1.5rem;
  }

  .empty-icon {
    color: var(--accent);
    margin-bottom: 0.75rem;
    opacity: 0.8;
  }

  .empty-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.375rem;
    letter-spacing: -0.01em;
  }

  .empty-description {
    color: var(--text-secondary);
    max-width: 320px;
    font-size: 0.875rem;
  }

  .empty-actions {
    margin-top: 1.5rem;
  }
</style>
```

### `src/lib/components/Shared/ErrorState.svelte`

```svelte
<script lang="ts">
  let {
    message = 'Something went wrong.',
    onRetry
  }: {
    message?: string;
    onRetry?: () => void;
  } = $props();
</script>

<div class="error-state">
  <p class="error-message">{message}</p>
  {#if onRetry}
    <button class="retry-btn" onclick={onRetry}>Retry</button>
  {/if}
</div>

<style>
  .error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
  }

  .error-message {
    color: var(--error);
    font-size: 0.875rem;
    text-align: center;
  }

  .retry-btn {
    padding: 0.375rem 1rem;
    font-size: 0.8125rem;
    font-weight: 500;
    background-color: transparent;
    color: var(--accent);
    border: 1px solid var(--accent);
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.15s ease, color 0.15s ease;
  }

  .retry-btn:hover {
    background-color: var(--accent);
    color: white;
  }
</style>
```

---

## Phase 4: Input Component

### `src/lib/components/Input/PromptInput.svelte`

```svelte
<script lang="ts">
  import Spinner from '$lib/components/Shared/Spinner.svelte';

  let {
    onSend,
    disabled = false
  }: {
    onSend: (message: string) => void;
    disabled?: boolean;
  } = $props();

  let inputValue = $state('');
  let textarea: HTMLTextAreaElement | undefined = $state();

  function handleSubmit(): void {
    if (!inputValue.trim() || disabled) return;
    onSend(inputValue);
    inputValue = '';
    resetTextareaHeight();
  }

  function handleKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  }

  function autoResize(): void {
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
    }
  }

  function resetTextareaHeight(): void {
    if (textarea) {
      textarea.style.height = 'auto';
    }
  }

  $effect(() => {
    inputValue;
    autoResize();
  });
</script>

<div class="input-container">
  <div class="input-wrapper">
    <textarea
      bind:this={textarea}
      bind:value={inputValue}
      onkeydown={handleKeydown}
      placeholder="Ask about scholarly publications..."
      rows="1"
      {disabled}
    ></textarea>
    <button
      class="send-btn"
      onclick={handleSubmit}
      disabled={!inputValue.trim() || disabled}
      title="Send message"
      aria-label="Send message"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="m22 2-7 20-4-9-9-4Z"></path>
        <path d="M22 2 11 13"></path>
      </svg>
    </button>
  </div>
  <p class="hint">
    Press <kbd>Enter</kbd> to send, <kbd>Shift + Enter</kbd> for new line
  </p>
</div>

<style>
  .input-container {
    padding: 0.75rem 1rem;
    background-color: var(--bg-primary);
    border-top: 1px solid var(--border);
  }

  .input-wrapper {
    display: flex;
    align-items: flex-end;
    gap: 0.5rem;
    max-width: 900px;
    margin: 0 auto;
    padding: 0.5rem 0.625rem;
    background-color: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 8px;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }

  .input-wrapper:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-light);
  }

  textarea {
    flex: 1;
    padding: 0.375rem 0.25rem;
    background-color: transparent;
    border: none;
    color: var(--text-primary);
    font-size: 0.875rem;
    font-family: inherit;
    resize: none;
    outline: none;
    line-height: 1.5;
    max-height: 150px;
  }

  textarea::placeholder {
    color: var(--text-muted);
  }

  textarea:disabled {
    opacity: 0.5;
  }

  .send-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background-color: var(--accent);
    border: none;
    border-radius: 6px;
    color: white;
    cursor: pointer;
    transition: background-color 0.15s ease;
    flex-shrink: 0;
  }

  .send-btn:hover:not(:disabled) {
    background-color: var(--accent-hover);
  }

  .send-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .send-btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }

  .hint {
    text-align: center;
    font-size: 0.6875rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
  }

  kbd {
    padding: 0.0625rem 0.25rem;
    background-color: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 3px;
    font-family: inherit;
    font-size: 0.625rem;
    color: var(--text-secondary);
  }
</style>
```

---

## Phase 5: Conversation Components

### `src/lib/components/Conversation/UserMessage.svelte`

```svelte
<script lang="ts">
  import type { ConversationTurn } from '$lib/types/exploration';

  let { message }: { message: ConversationTurn } = $props();

  function formatTime(date: Date): string {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
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
      <p>{message.content}</p>
    </div>
  </div>
</div>

<style>
  .message {
    display: flex;
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
    max-width: 70%;
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
    color: var(--text-primary);
    line-height: 1.5;
    font-size: 0.875rem;
  }

  .message-body p {
    margin: 0;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @media (max-width: 640px) {
    .content { max-width: 85%; }
    .message { padding: 0.625rem 0.75rem; }
  }
</style>
```

### `src/lib/components/Insights/ObservationCard.svelte`

```svelte
<script lang="ts">
  import type { Observation } from '$lib/types/exploration';
  import Badge from '$lib/components/Shared/Badge.svelte';

  let { observation }: { observation: Observation } = $props();
</script>

<div class="observation-card">
  <div class="observation-header">
    <Badge variant="accent">AI</Badge>
    <span class="observation-label">Interpretation</span>
  </div>
  <p class="observation-text">{observation.text}</p>
</div>

<style>
  .observation-card {
    padding: 0.75rem 1rem;
    background-color: var(--ai-interpretation-bg);
    border-left: 3px solid var(--ai-interpretation-border);
    border-radius: 0 6px 6px 0;
    margin-top: 0.625rem;
  }

  .observation-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.375rem;
  }

  .observation-label {
    font-size: 0.6875rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .observation-text {
    font-size: 0.8125rem;
    color: var(--text-primary);
    line-height: 1.5;
    margin: 0;
  }
</style>
```

### `src/lib/components/Insights/SuggestionChips.svelte`

```svelte
<script lang="ts">
  import type { FollowUpQuestion } from '$lib/types/exploration';

  let {
    suggestions,
    onSelect
  }: {
    suggestions: FollowUpQuestion[];
    onSelect: (suggestion: FollowUpQuestion) => void;
  } = $props();
</script>

{#if suggestions.length > 0}
  <div class="suggestions">
    <p class="suggestions-label">You could explore:</p>
    <div class="suggestions-list">
      {#each suggestions as suggestion (suggestion.id)}
        <button class="suggestion-chip" onclick={() => onSelect(suggestion)}>
          {suggestion.text}
        </button>
      {/each}
    </div>
  </div>
{/if}

<style>
  .suggestions {
    margin-top: 0.75rem;
  }

  .suggestions-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
  }

  .suggestions-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.375rem;
  }

  .suggestion-chip {
    padding: 0.3125rem 0.75rem;
    font-size: 0.8125rem;
    font-family: inherit;
    background-color: transparent;
    color: var(--accent);
    border: 1px solid var(--border);
    border-radius: 9999px;
    cursor: pointer;
    transition: background-color 0.15s ease, border-color 0.15s ease;
    white-space: nowrap;
  }

  .suggestion-chip:hover {
    background-color: var(--accent-light);
    border-color: var(--accent);
  }

  .suggestion-chip:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
</style>
```

### `src/lib/components/Conversation/AssistantMessage.svelte`

```svelte
<script lang="ts">
  import type { ConversationTurn, ResultState, Observation, FollowUpQuestion } from '$lib/types/exploration';
  import Spinner from '$lib/components/Shared/Spinner.svelte';
  import ExplorationRenderer from '$lib/components/Results/ExplorationRenderer.svelte';
  import ObservationCard from '$lib/components/Insights/ObservationCard.svelte';
  import SuggestionChips from '$lib/components/Insights/SuggestionChips.svelte';

  let {
    message,
    result,
    observations,
    suggestions,
    onSelectSuggestion
  }: {
    message: ConversationTurn;
    result: ResultState | null;
    observations: Observation[];
    suggestions: FollowUpQuestion[];
    onSelectSuggestion: (suggestion: FollowUpQuestion) => void;
  } = $props();

  function formatTime(date: Date): string {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
</script>

<div class="message assistant" class:error={message.error}>
  <div class="avatar">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>
  </div>

  <div class="content">
    <div class="message-header">
      <span class="role">Assistant</span>
      <span class="time">{formatTime(message.timestamp)}</span>
    </div>

    <div class="message-body">
      {#if message.loading}
        <div class="loading">
          <Spinner size={14} />
          <span>Thinking about the question...</span>
        </div>
      {:else if message.content}
        <p>{message.content}</p>
      {/if}

      {#if result && !message.loading && !message.error}
        <ExplorationRenderer {result} />
      {/if}

      {#if observations.length > 0 && !message.loading}
        {#each observations as observation (observation.id)}
          <ObservationCard {observation} />
        {/each}
      {/if}

      {#if suggestions.length > 0 && !message.loading}
        <SuggestionChips {suggestions} onSelect={onSelectSuggestion} />
      {/if}

      {#if message.error}
        <p class="error-text">Please try again or rephrase your question.</p>
      {/if}
    </div>
  </div>
</div>

<style>
  .message {
    display: flex;
    gap: 0.625rem;
    padding: 0.75rem 1rem;
    animation: fadeIn 0.2s ease-out;
  }

  .message.error .content {
    border: 1px solid var(--error);
  }

  .avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    background-color: var(--bg-tertiary);
    color: var(--text-secondary);
  }

  .content {
    max-width: 80%;
    padding: 0.625rem 0.875rem;
    background-color: var(--assistant-bubble);
    border-radius: 12px 12px 12px 2px;
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
    color: var(--text-primary);
    line-height: 1.5;
    font-size: 0.875rem;
  }

  .message-body p {
    margin: 0;
  }

  .loading {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-secondary);
    font-size: 0.8125rem;
  }

  .error-text {
    color: var(--error);
    font-size: 0.8125rem;
    margin-top: 0.5rem;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @media (max-width: 640px) {
    .content { max-width: 90%; }
    .message { padding: 0.625rem 0.75rem; }
  }
</style>
```

### `src/lib/components/Conversation/ConversationView.svelte`

```svelte
<script lang="ts">
  import type { ConversationTurn, ResultState, Observation, FollowUpQuestion } from '$lib/types/exploration';
  import UserMessage from './UserMessage.svelte';
  import AssistantMessage from './AssistantMessage.svelte';
  import EmptyState from '$lib/components/Shared/EmptyState.svelte';

  let {
    conversation,
    results,
    observations,
    suggestions,
    onSelectSuggestion
  }: {
    conversation: ConversationTurn[];
    results: Map<string, ResultState>;
    observations: Map<string, Observation[]>;
    suggestions: Map<string, FollowUpQuestion[]>;
    onSelectSuggestion: (suggestion: FollowUpQuestion) => void;
  } = $props();

  let container: HTMLDivElement | undefined = $state();

  $effect(() => {
    conversation.length;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  });
</script>

<div class="conversation-container" bind:this={container}>
  {#if conversation.length === 0}
    <EmptyState
      title="Welcome to Scholarly Explorer"
      description="Ask me about authors, venues, and publications in the knowledge graph."
    >
      {#snippet icon()}
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      {/snippet}
      <div class="examples">
        <p class="examples-title">Try asking:</p>
        <ul>
          <li>"Who are the most prolific authors?"</li>
          <li>"Which venues do they publish in?"</li>
          <li>"Show me publication trends over time"</li>
        </ul>
      </div>
    </EmptyState>
  {:else}
    {#each conversation as turn (turn.id)}
      {#if turn.role === 'user'}
        <UserMessage message={turn} />
      {:else}
        <AssistantMessage
          message={turn}
          result={results.get(turn.id) || null}
          observations={observations.get(turn.id) || []}
          suggestions={suggestions.get(turn.id) || []}
          {onSelectSuggestion}
        />
      {/if}
    {/each}
  {/if}
</div>

<style>
  .conversation-container {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    background-color: var(--bg-secondary);
  }

  .examples {
    margin-top: 1.5rem;
    padding: 0.875rem;
    background-color: var(--bg-primary);
    border-radius: 6px;
    border: 1px solid var(--border);
    text-align: left;
    max-width: 320px;
  }

  .examples-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .examples ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .examples li {
    padding: 0.3125rem 0;
    font-size: 0.8125rem;
    color: var(--text-secondary);
  }

  @media (max-width: 640px) {
    .conversation-container { padding: 0.75rem; }
    .examples { max-width: 100%; }
  }
</style>
```

---

## Phase 6: Result View Components

### `src/lib/components/Results/ExplorationRenderer.svelte`

Routes to the correct view based on result type.

```svelte
<script lang="ts">
  import type { ResultState } from '$lib/types/exploration';
  import FacetTable from './FacetTable.svelte';
  import ComparisonView from './ComparisonView.svelte';
  import TimelineView from './TimelineView.svelte';
  import SummaryView from './SummaryView.svelte';

  let { result }: { result: ResultState } = $props();
</script>

{#if result.type === 'facet_table' || result.type === 'entity_list'}
  <FacetTable columns={result.columns} rows={result.rows} title={result.title} />
{:else if result.type === 'comparison'}
  <ComparisonView columns={result.columns} rows={result.rows} title={result.title} />
{:else if result.type === 'timeline'}
  <TimelineView columns={result.columns} rows={result.rows} title={result.title} />
{:else if result.type === 'summary'}
  <SummaryView title={result.title} />
{/if}
```

### `src/lib/components/Results/FacetTable.svelte`

```svelte
<script lang="ts">
  import type { ResultColumn, ResultRow, SortState } from '$lib/types/exploration';

  let {
    columns,
    rows,
    title,
    onSort
  }: {
    columns: ResultColumn[];
    rows: ResultRow[];
    title?: string;
    onSort?: (sort: SortState) => void;
  } = $props();

  let sortField = $state<string | null>(null);
  let sortDirection = $state<'asc' | 'desc'>('asc');

  function handleSort(column: ResultColumn): void {
    if (!column.sortable) return;
    if (sortField === column.key) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortField = column.key;
      sortDirection = 'asc';
    }
    onSort?.({ field: sortField, direction: sortDirection });
  }

  let sortedRows = $derived.by(() => {
    if (!sortField) return rows;
    return [...rows].sort((a, b) => {
      const aVal = a[sortField!];
      const bVal = b[sortField!];
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
      const cmp = String(aVal).localeCompare(String(bVal));
      return sortDirection === 'asc' ? cmp : -cmp;
    });
  });
</script>

<div class="table-container">
  {#if title}
    <div class="table-header">
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
        <line x1="3" x2="21" y1="9" y2="9"></line>
        <line x1="3" x2="21" y1="15" y2="15"></line>
        <line x1="9" x2="9" y1="3" y2="21"></line>
        <line x1="15" x2="15" y1="3" y2="21"></line>
      </svg>
      <span>{title}</span>
    </div>
  {/if}

  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          {#each columns as column}
            <th
              class:sortable={column.sortable}
              class:sorted={sortField === column.key}
              onclick={() => handleSort(column)}
            >
              <span class="th-content">
                {column.label}
                {#if sortField === column.key}
                  <span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                {/if}
              </span>
            </th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each sortedRows as row, i (i)}
          <tr>
            {#each columns as column}
              <td>
                {#if column.type === 'badge'}
                  <span class="cell-badge">{row[column.key]}</span>
                {:else}
                  {row[column.key]}
                {/if}
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>

<style>
  .table-container {
    margin-top: 0.625rem;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--code-border);
  }

  .table-header {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.625rem;
    background-color: var(--bg-secondary);
    border-bottom: 1px solid var(--code-border);
    font-size: 0.6875rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .table-wrapper {
    overflow-x: auto;
    background-color: var(--bg-primary);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8125rem;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  }

  th, td {
    padding: 0.5rem 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border-light);
    white-space: nowrap;
  }

  th {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    font-weight: 600;
    position: sticky;
    top: 0;
    font-size: 0.75rem;
  }

  th.sortable {
    cursor: pointer;
    user-select: none;
  }

  th.sortable:hover {
    background-color: var(--bg-tertiary);
  }

  th.sorted {
    color: var(--accent);
  }

  .th-content {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
  }

  .sort-indicator {
    font-size: 0.625rem;
  }

  td {
    color: var(--text-primary);
  }

  tr:last-child td {
    border-bottom: none;
  }

  tbody tr:hover td {
    background-color: var(--bg-secondary);
  }

  tbody tr {
    transition: background-color 0.1s ease;
  }

  .cell-badge {
    display: inline-block;
    padding: 0.0625rem 0.375rem;
    font-size: 0.6875rem;
    font-weight: 500;
    background-color: var(--bg-tertiary);
    border-radius: 9999px;
    color: var(--text-secondary);
  }
</style>
```

### `src/lib/components/Results/ComparisonView.svelte`

```svelte
<script lang="ts">
  import type { ResultColumn, ResultRow } from '$lib/types/exploration';

  let {
    columns,
    rows,
    title
  }: {
    columns: ResultColumn[];
    rows: ResultRow[];
    title?: string;
  } = $props();
</script>

<div class="comparison-container">
  {#if title}
    <div class="comparison-header">{title}</div>
  {/if}

  <div class="comparison-table-wrapper">
    <table>
      <thead>
        <tr>
          {#each columns as column}
            <th>{column.label}</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each rows as row, i (i)}
          <tr>
            {#each columns as column, j}
              <td class:metric-cell={j === 0}>{row[column.key]}</td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>

<style>
  .comparison-container {
    margin-top: 0.625rem;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--code-border);
  }

  .comparison-header {
    padding: 0.375rem 0.625rem;
    background-color: var(--bg-secondary);
    border-bottom: 1px solid var(--code-border);
    font-size: 0.6875rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .comparison-table-wrapper {
    overflow-x: auto;
    background-color: var(--bg-primary);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8125rem;
  }

  th, td {
    padding: 0.5rem 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border-light);
  }

  th {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    font-weight: 600;
    font-size: 0.75rem;
  }

  .metric-cell {
    font-weight: 500;
    color: var(--text-secondary);
    font-size: 0.75rem;
  }

  tr:last-child td {
    border-bottom: none;
  }

  tbody tr:hover td {
    background-color: var(--bg-secondary);
  }
</style>
```

### `src/lib/components/Results/TimelineView.svelte`

Simple bar chart representation using CSS.

```svelte
<script lang="ts">
  import type { ResultColumn, ResultRow } from '$lib/types/exploration';

  let {
    columns,
    rows,
    title
  }: {
    columns: ResultColumn[];
    rows: ResultRow[];
    title?: string;
  } = $props();

  // First column is the label (year), rest are data series
  let labelColumn = $derived(columns[0]);
  let dataColumns = $derived(columns.slice(1));

  let maxValue = $derived.by(() => {
    let max = 0;
    for (const row of rows) {
      for (const col of dataColumns) {
        const val = Number(row[col.key]) || 0;
        if (val > max) max = val;
      }
    }
    return max;
  });
</script>

<div class="timeline-container">
  {#if title}
    <div class="timeline-header">{title}</div>
  {/if}

  <div class="timeline-body">
    {#each rows as row, i (i)}
      <div class="timeline-row">
        <span class="timeline-label">{row[labelColumn.key]}</span>
        <div class="timeline-bars">
          {#each dataColumns as col}
            <div class="bar-group">
              <div
                class="bar"
                style="width: {((Number(row[col.key]) || 0) / maxValue) * 100}%"
              ></div>
              <span class="bar-value">{row[col.key]}</span>
            </div>
          {/each}
        </div>
      </div>
    {/each}
  </div>

  {#if dataColumns.length > 1}
    <div class="timeline-legend">
      {#each dataColumns as col}
        <span class="legend-item">
          <span class="legend-dot"></span>
          {col.label}
        </span>
      {/each}
    </div>
  {/if}
</div>

<style>
  .timeline-container {
    margin-top: 0.625rem;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--code-border);
    background-color: var(--bg-primary);
  }

  .timeline-header {
    padding: 0.375rem 0.625rem;
    background-color: var(--bg-secondary);
    border-bottom: 1px solid var(--code-border);
    font-size: 0.6875rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .timeline-body {
    padding: 0.75rem;
  }

  .timeline-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }

  .timeline-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-secondary);
    min-width: 2.5rem;
    text-align: right;
  }

  .timeline-bars {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.125rem;
  }

  .bar-group {
    display: flex;
    align-items: center;
    gap: 0.375rem;
  }

  .bar {
    height: 12px;
    background-color: var(--accent);
    border-radius: 2px;
    min-width: 2px;
    transition: width 0.3s ease;
  }

  .bar-value {
    font-size: 0.6875rem;
    color: var(--text-muted);
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  }

  .timeline-legend {
    display: flex;
    gap: 1rem;
    padding: 0.5rem 0.75rem;
    border-top: 1px solid var(--border-light);
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.6875rem;
    color: var(--text-secondary);
  }

  .legend-dot {
    width: 8px;
    height: 8px;
    background-color: var(--accent);
    border-radius: 2px;
  }
</style>
```

### `src/lib/components/Results/SummaryView.svelte`

```svelte
<script lang="ts">
  let { title }: { title?: string } = $props();
</script>

{#if title}
  <div class="summary-container">
    <p class="summary-text">{title}</p>
  </div>
{/if}

<style>
  .summary-container {
    margin-top: 0.625rem;
    padding: 0.75rem 1rem;
    background-color: var(--bg-primary);
    border: 1px solid var(--border-light);
    border-radius: 6px;
  }

  .summary-text {
    font-size: 0.8125rem;
    color: var(--text-primary);
    line-height: 1.5;
    margin: 0;
  }
</style>
```

---

## Phase 8: Main Page

### `src/routes/+page.svelte`

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import ConversationView from '$lib/components/Conversation/ConversationView.svelte';
  import PromptInput from '$lib/components/Input/PromptInput.svelte';
  import { exploration } from '$lib/stores/exploration.svelte';
  import { decodeStateFromUrl } from '$lib/utils/persistence';

  let initialized = $state(false);

  onMount(() => {
    const urlState = decodeStateFromUrl(page.url.searchParams);

    if (urlState.q) {
      exploration.sendMessage(urlState.q);
    } else {
      exploration.loadState();
    }

    initialized = true;
  });

  let resultsMap = $derived(exploration.resultsByTurn);
  let observationsMap = $derived(exploration.observationsByTurn);
  let suggestionsMap = $derived(exploration.suggestionsByTurn);
</script>

<svelte:head>
  <title>Scholarly Explorer</title>
  <meta name="description" content="Explore scholarly knowledge graphs through conversation" />
</svelte:head>

<div class="app">
  <header class="app-header">
    <h1 class="app-title">Scholarly Explorer</h1>
    {#if exploration.conversation.length > 0}
      <button class="clear-btn" onclick={() => exploration.clearExploration()}>
        New Exploration
      </button>
    {/if}
  </header>

  <ConversationView
    conversation={exploration.conversation}
    results={resultsMap}
    observations={observationsMap}
    suggestions={suggestionsMap}
    onSelectSuggestion={(s) => exploration.selectSuggestion(s)}
  />

  <PromptInput
    onSend={(msg) => exploration.sendMessage(msg)}
    disabled={exploration.loading}
  />
</div>

<style>
  .app {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
  }

  .app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    background-color: var(--bg-primary);
    border-bottom: 1px solid var(--border);
  }

  .app-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
  }

  .clear-btn {
    padding: 0.3125rem 0.75rem;
    font-size: 0.8125rem;
    font-weight: 500;
    font-family: inherit;
    background-color: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border);
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.15s ease, color 0.15s ease;
  }

  .clear-btn:hover {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
  }

  .clear-btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
</style>
```

---

## Phase 9: Visual Polish & Design System Compliance

### Checklist:

- [ ] All colors use CSS custom properties — no arbitrary hex values
- [ ] Typography hierarchy: page title bold, section headings semibold, body regular, metadata small+muted
- [ ] Spacing: tight for metadata, standard for controls, medium for content groups
- [ ] Tables: muted header bg, small type, sticky headers, subtle row hover, monospace for data
- [ ] Buttons: primary for send, secondary for suggestions/pivots, icon-only only when unambiguous
- [ ] Badges for "AI interpretation", entity types
- [ ] Cards for observations (subtle border, moderate radius, comfortable padding)
- [ ] Focus states: accent ring on all interactive elements
- [ ] Responsive: mobile-first, single column on small screens, wider content on desktop
- [ ] Data vs LLM distinction: observations have left accent border + "AI" badge + blue tint
- [ ] No unnecessary animations — only fadeIn for new messages, spin for loading
- [ ] Consistent border radius: small for inputs/buttons (6px), medium for cards/tables (6px), full for pills/badges

---

## Phase 10: Keyboard & Accessibility

- [ ] Tab order: header → conversation → suggestions → input
- [ ] Enter/Space activates suggestion chips and table rows
- [ ] Escape clears entity selection
- [ ] `:focus-visible` accent ring on all interactive elements
- [ ] `aria-label` on icon-only buttons (send, close, sort)
- [ ] `aria-live="polite"` on conversation container
- [ ] Semantic HTML: `<header>`, `<main>`, `<table>`, `<button>`
- [ ] Screen reader text for loading states

---

## Phase 11: URL & Session State (P1)

### Steps:

1. Serialize key state to URL search params using SvelteKit's `page` store:
   - `?q=` — last user query
   - `&facet=` — target facet

2. On page load (`+page.ts` load function), read URL params and restore initial state

3. Persist full conversation to `sessionStorage` as JSON

4. Update URL on each exploration state change using `goto()` from `$app/navigation`

---

## Phase 9: Persistence Utility

**Goal:** Session storage and URL state management for exploration recovery.

### `src/lib/utils/persistence.ts`

```typescript
import type {
  ConversationTurn,
  Facet,
  SortState,
  ResultState,
  Observation,
  FollowUpQuestion
} from '$lib/types/exploration';

const STORAGE_KEY = 'scholarly-explorer-state';

export interface PersistedState {
  conversation: ConversationTurn[];
  targetFacet: Facet | null;
  sorting: SortState | null;
  result: ResultState | null;
  observations: Observation[];
  suggestions: FollowUpQuestion[];
  resultsByTurn?: Record<string, ResultState>;
  observationsByTurn?: Record<string, Observation[]>;
  suggestionsByTurn?: Record<string, FollowUpQuestion[]>;
}

interface SerializedConversationTurn {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  loading?: boolean;
  error?: boolean;
}

export function serializeConversation(turns: ConversationTurn[]): SerializedConversationTurn[] {
  return turns.map((turn) => ({
    id: turn.id,
    role: turn.role,
    content: turn.content,
    timestamp: turn.timestamp.toISOString(),
    loading: turn.loading,
    error: turn.error
  }));
}

export function deserializeConversation(
  turns: SerializedConversationTurn[]
): ConversationTurn[] {
  return turns.map((turn) => ({
    id: turn.id,
    role: turn.role,
    content: turn.content,
    timestamp: new Date(turn.timestamp),
    loading: turn.loading,
    error: turn.error
  }));
}

export function saveToSessionStorage(state: {
  conversation: ConversationTurn[];
  targetFacet: Facet | null;
  sorting: SortState | null;
  result: ResultState | null;
  observations: Observation[];
  suggestions: FollowUpQuestion[];
  resultsByTurn?: Record<string, ResultState>;
  observationsByTurn?: Record<string, Observation[]>;
  suggestionsByTurn?: Record<string, FollowUpQuestion[]>;
}): void {
  try {
    const serialized = {
      conversation: serializeConversation(state.conversation),
      targetFacet: state.targetFacet,
      sorting: state.sorting,
      result: state.result,
      observations: state.observations,
      suggestions: state.suggestions,
      resultsByTurn: state.resultsByTurn,
      observationsByTurn: state.observationsByTurn,
      suggestionsByTurn: state.suggestionsByTurn
    };
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(serialized));
  } catch {
    console.warn('Failed to save state to sessionStorage');
  }
}

export function loadFromSessionStorage(): PersistedState | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;

    const parsed = JSON.parse(raw);
    return {
      conversation: deserializeConversation(parsed.conversation || []),
      targetFacet: parsed.targetFacet || null,
      sorting: parsed.sorting || null,
      result: parsed.result || null,
      observations: parsed.observations || [],
      suggestions: parsed.suggestions || [],
      resultsByTurn: parsed.resultsByTurn || {},
      observationsByTurn: parsed.observationsByTurn || {},
      suggestionsByTurn: parsed.suggestionsByTurn || {}
    };
  } catch {
    console.warn('Failed to load state from sessionStorage');
    return null;
  }
}

export function clearSessionStorage(): void {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    console.warn('Failed to clear sessionStorage');
  }
}

export function encodeStateToUrl(params: {
  q?: string;
  facet?: Facet;
}): URLSearchParams {
  const searchParams = new URLSearchParams();

  if (params.q) {
    searchParams.set('q', params.q);
  }
  if (params.facet) {
    searchParams.set('facet', params.facet);
  }

  return searchParams;
}

export function decodeStateFromUrl(searchParams: URLSearchParams): {
  q?: string;
  facet?: Facet;
} {
  const result: {
    q?: string;
    facet?: Facet;
  } = {};

  const q = searchParams.get('q');
  if (q) {
    result.q = q;
  }

  const facet = searchParams.get('facet');
  if (facet && isValidFacet(facet)) {
    result.facet = facet;
  }

  return result;
}

function isValidFacet(value: string): value is Facet {
  return ['author', 'venue', 'year', 'publication'].includes(value);
}
```

---

## File Structure Summary

```
frontend/adaptive/
├── src/
│   ├── app.css
│   ├── app.html
│   ├── app.d.ts
│   ├── routes/
│   │   ├── +layout.svelte
│   │   └── +page.svelte
│   └── lib/
│       ├── types/
│       │   └── exploration.ts
│       ├── data/
│       │   ├── mock-responses.ts
│       │   └── mock-entities.ts
│       ├── stores/
│       │   └── exploration.svelte.ts
│       ├── utils/
│       │   └── persistence.ts
│       └── components/
│           ├── Conversation/
│           │   ├── ConversationView.svelte
│           │   ├── UserMessage.svelte
│           │   └── AssistantMessage.svelte
│           ├── Results/
│           │   ├── ExplorationRenderer.svelte
│           │   ├── FacetTable.svelte
│           │   ├── ComparisonView.svelte
│           │   ├── TimelineView.svelte
│           │   └── SummaryView.svelte
│           ├── Insights/
│           │   ├── ObservationCard.svelte
│           │   └── SuggestionChips.svelte
│           ├── Input/
│           │   └── PromptInput.svelte
│           └── Shared/
│               ├── Badge.svelte
│               ├── Spinner.svelte
│               ├── EmptyState.svelte
│               └── ErrorState.svelte
├── static/
│   └── favicon.svg
├── TEST-PLAN.md
├── TEST-REPORT.md
├── package.json
├── svelte.config.js
├── tsconfig.json
└── vite.config.ts
```

---

## Implementation Order

| Step | Task | Dependencies | Est. Effort |
|------|------|-------------|-------------|
| 1 | Scaffold SvelteKit project | None | 30 min |
| 2 | Create `app.css` with design tokens | Step 1 | 30 min |
| 3 | Create `exploration.ts` type definitions | Step 1 | 45 min |
| 4 | Create mock data files | Step 3 | 1 hr |
| 5 | Create `exploration.svelte.ts` store | Steps 3, 4 | 1.5 hr |
| 6 | Create Shared components (Badge, Pill, Spinner, EmptyState, ErrorState) | Step 2 | 1 hr |
| 7 | Create PromptInput component | Step 6 | 30 min |
| 8 | Create UserMessage component | Step 6 | 30 min |
| 9 | Create FacetTable component | Step 6 | 1 hr |
| 10 | Create ExplorationRenderer + remaining result views | Steps 6, 9 | 1.5 hr |
| 11 | Create ObservationCard + SuggestionChips | Step 6 | 45 min |
| 12 | Create AssistantMessage component | Steps 8, 10, 11 | 1 hr |
| 13 | Create ConversationView | Steps 8, 12 | 45 min |
| 14 | Create persistence utility | Step 3 | 45 min |
| 15 | Wire up `+page.svelte` | Steps 5, 7, 13, 14 | 45 min |
| 17 | Add direct manipulation interactions | Step 16 | 1.5 hr |
| 18 | Visual polish & responsive design | Step 16 | 1 hr |
| 19 | Keyboard accessibility | Step 17 | 1 hr |
| 20 | URL/session persistence | Step 16 | 1 hr |
| 21 | Final testing & bug fixes | All | 1 hr |

**Total estimated effort: ~18 hours**

---

## Implementation Learnings

### 1. Per-Turn Data Storage is Essential

**Problem:** The original plan stored a single `result`, `observations`, and `suggestions` that got overwritten on each new message. This caused previous responses to lose their data when a new message was sent.

**Solution:** Added per-turn storage using Maps keyed by conversation turn ID:
- `resultsByTurn: Map<string, ResultState>`
- `observationsByTurn: Map<string, Observation[]>`
- `suggestionsByTurn: Map<string, FollowUpQuestion[]>`

**Lesson:** In conversational UIs, each turn's context must be preserved independently. Never overwrite previous turn data.

### 2. WCAG AA Color Compliance

**Problem:** The original `--text-muted: #adb5bd` had ~3:1 contrast ratio, failing WCAG AA (requires 4.5:1).

**Solution:** Changed to `--text-muted: #6c757d` which achieves ~5:1 contrast ratio.

**Lesson:** Always verify color contrast early. Muted/de-emphasized text still needs to meet accessibility standards.

### 3. ConversationTurn.svelte Was Unnecessary

**Problem:** The plan included a separate `ConversationTurn.svelte` component that was never created. The routing logic was merged into `ConversationView.svelte`.

**Lesson:** Don't create components until you need them. The routing can be handled inline in the parent component.

### 4. Session Persistence Needs Map ↔ Record Conversion

**Problem:** `JSON.stringify` doesn't handle `Map` objects. Per-turn Maps needed conversion to/from plain objects.

**Solution:** Used `Object.fromEntries(map)` for serialization and `new Map(Object.entries(obj))` for deserialization.

**Lesson:** Always test serialization with complex data structures. Maps, Sets, and Dates need special handling.

---

## Test Results

- **Test Plan:** 65 test cases across 12 suites
- **Test Report:** 96.9% pass rate (63/65 passed)
- **Bugs Found:** 2 (1 medium: contrast, 1 low: test plan typo)
- **Bugs Fixed:** 1 (contrast issue fixed)
- **Browser Tested:** Chromium (Chrome 151) via Playwright
- **Responsive:** Desktop (1920x1080), Tablet (768px), Mobile (375px)
