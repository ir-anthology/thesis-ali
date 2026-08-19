# Implementation Plan: Exploratory Search UI

## Overview

Replace the existing chat-based UI with a three-panel exploratory search interface for LLM-Assisted Exploratory Search in Scholarly Knowledge Graphs.

**Stack:** SvelteKit 5 (runes) + Tailwind CSS 4 + TypeScript

**Data:** Static/hardcoded mock data for all components (no backend integration yet).

---

## High-Level Layout

```
+------------------------------------------------------------------+
|                       Application Header                         |
+------------------------------------------------------------------+
|  +------------------------------------------------------------+  |
|  | Ask the research question...                         [->]  |  |
|  +------------------------------------------------------------+  |
+-------------------------------------------+----------------------+
|           FACETED SEARCH TABLE            |   OBSERVATIONS       |
|                                           |                      |
|  Target: Authors                          |   - Insight 1        |
|                                           |   - Insight 2        |
|  Author       Venues   Years   Papers     |                      |
|  --------------------------------------   |   Follow-up:         |
|  Author A       12       5       42       |   [Question 1]       |
|  Author B        8       4       31       |   [Question 2]       |
|  Author C        6       3       25       |   [Question 3]       |
+-------------------------------------------+----------------------+
```

---

## File Structure

```
src/
+-- app.css                              (modify -- add design tokens)
+-- lib/
|   +-- types/
|   |   +-- exploration.ts               (NEW)
|   +-- data/
|   |   +-- mock-data.ts                 (NEW)
|   +-- stores/
|   |   +-- exploration.svelte.ts        (NEW)
|   +-- api/
|   |   +-- client.ts                    (modify -- add mock functions)
|   +-- components/
|       +-- Header.svelte                (NEW)
|       +-- SearchPanel.svelte           (NEW)
|       +-- ExplorationWorkspace.svelte  (NEW)
|       +-- FacetToolbar.svelte          (NEW)
|       +-- ActiveFilters.svelte         (NEW)
|       +-- FacetTable.svelte            (NEW)
|       +-- FacetCell.svelte             (NEW)
|       +-- InsightsPanel.svelte         (NEW)
|       +-- ObservationItem.svelte       (NEW)
|       +-- FollowUpButton.svelte        (NEW)
|       +-- PromptTooltip.svelte         (NEW)
|       +-- LoadingState.svelte          (NEW)
|       +-- UnsupportedState.svelte      (NEW)
|       +-- ErrorState.svelte            (NEW)
|       +-- ChatHeader.svelte            (DELETE)
|       +-- ChatInput.svelte             (DELETE)
|       +-- ChatMessage.svelte           (DELETE)
|       +-- SparqlCodeBlock.svelte       (DELETE)
|       +-- TableResult.svelte           (DELETE)
+-- routes/
    +-- +page.svelte                     (modify -- new layout)
```

---

## Implementation Steps

Execute these steps in order. Each step lists the file, what to create/modify, and the key details.

---

### Step 1: Type Definitions

**File:** `src/lib/types/exploration.ts` (CREATE)

Define all core types used across the application:

```typescript
export type Facet = 'author' | 'venue' | 'year' | 'publication';

export interface Filter {
  field: Facet;
  operator: '=' | '>=' | '<=';
  value: string | number;
}

export interface FacetRow {
  targetValue: string | number;
  connections: Record<Facet, number | string>;
}

export interface SortState {
  facet: Facet;
  direction: 'asc' | 'desc';
}

export interface Observation {
  id: string;
  text: string;
}

export interface FollowUpQuestion {
  id: string;
  text: string;
}

export type LoadingStage =
  | 'interpreting'
  | 'preparing'
  | 'querying'
  | 'analyzing'
  | null;

export type ErrorType = 'generic' | 'unavailable' | 'unsupported';

export interface ErrorState {
  type: ErrorType;
  message: string;
  suggestions?: string[];
}

export interface GeneratedPrompt {
  text: string;
  targetCell?: { rowIndex: number; facet: Facet };
}

export interface ExplorationState {
  input: string;
  targetFacet: Facet | null;
  filters: Filter[];
  sorting: SortState | null;
  rows: FacetRow[];
  observations: Observation[];
  followUpQuestions: FollowUpQuestion[];
  loadingStage: LoadingStage;
  error: ErrorState | null;
  promptOutputMode: 'input' | 'tooltip';
  generatedPrompt: GeneratedPrompt | null;
  hasSubmitted: boolean;
}
```

---

### Step 2: Mock Data

**File:** `src/lib/data/mock-data.ts` (CREATE)

Provide hardcoded data for all exploration states. Use generic placeholder names (not real DBLP data).

#### 2a. Initial Summary (before any target facet is selected)

Shows aggregate counts for each facet:

```
Authors: 1245 | Venues: 320 | Years: 35 | Publications: 250000
```

This is a single summary row, not expandable.

#### 2b. Authors Target Facet (default query result)

| Author   | Venues | Years | Publications |
|----------|--------|-------|-------------|
| Author A | 12     | 5     | 42          |
| Author B | 8      | 4     | 31          |
| Author C | 6      | 3     | 25          |
| Author D | 15     | 7     | 58          |
| Author E | 4      | 2     | 12          |
| Author F | 9      | 6     | 37          |
| Author G | 3      | 2     | 8           |
| Author H | 11     | 5     | 44          |
| Author I | 7      | 4     | 29          |
| Author J | 5      | 3     | 18          |

Each row is a `FacetRow`:

```typescript
{
  targetValue: 'Author A',
  connections: {
    author: 'Author A',   // self-reference
    venue: 12,            // number of distinct venues
    year: 5,              // number of distinct years
    publication: 42       // number of publications
  }
}
```

#### 2c. Venues Target Facet

| Venue         | Authors | Years | Publications |
|---------------|---------|-------|-------------|
| Venue Alpha   | 240     | 15    | 1200        |
| Venue Beta    | 180     | 12    | 890         |
| Venue Gamma   | 95      | 8     | 420         |
| Venue Delta   | 60      | 6     | 280         |
| Venue Epsilon | 45      | 4     | 150         |

#### 2d. Years Target Facet

| Year | Authors | Venues | Publications |
|------|---------|--------|-------------|
| 2025 | 320     | 45     | 2800        |
| 2024 | 580     | 120    | 8500        |
| 2023 | 520     | 110    | 7800        |
| 2022 | 480     | 100    | 7200        |
| 2021 | 430     | 90     | 6500        |
| 2020 | 390     | 85     | 5800        |

#### 2e. Filtered Results (pivot data)

When a user clicks a numeric cell, the table pivots. Prepare mock data for common pivot scenarios:

**Scenario 1:** Author A clicked on venues column

- Filter: `author = Author A`
- Target: `venue`

| Venue         | Years | Publications |
|---------------|-------|-------------|
| Venue Alpha   | 3     | 15          |
| Venue Beta    | 2     | 12          |
| Venue Gamma   | 2     | 8           |
| Venue Delta   | 1     | 4           |
| Venue Epsilon | 1     | 3           |

**Scenario 2:** Author A clicked on years column

- Filter: `author = Author A`
- Target: `year`

| Year | Venues | Publications |
|------|--------|-------------|
| 2025 | 3      | 12          |
| 2024 | 5      | 15          |
| 2023 | 4      | 10          |
| 2022 | 2      | 5           |

**Scenario 3:** Venue Alpha clicked on authors column

- Filter: `venue = Venue Alpha`
- Target: `author`

| Author   | Years | Publications |
|----------|-------|-------------|
| Author A | 3     | 15          |
| Author D | 5     | 22          |
| Author H | 4     | 18          |
| Author B | 2     | 8           |
| Author F | 3     | 11          |

#### 2f. Observations

```typescript
export const defaultObservations: Observation[] = [
  { id: '1', text: 'Author A and Author D are the most active contributors, with 42 and 58 publications respectively.' },
  { id: '2', text: 'Publication activity spans multiple venues, with Venue Alpha being the most frequent.' },
  { id: '3', text: 'There is a clear increasing trend in publications over recent years, peaking in 2024.' },
  { id: '4', text: 'Most authors publish across 3-6 distinct venues, suggesting interdisciplinary work.' }
];
```

#### 2g. Follow-up Questions

```typescript
export const defaultFollowUps: FollowUpQuestion[] = [
  { id: '1', text: 'How has publication output changed over time?' },
  { id: '2', text: 'Which venues have the most publications?' },
  { id: '3', text: 'Who are the most prolific authors?' },
  { id: '4', text: 'What are the recent trends in this area?' }
];
```

#### 2h. Unsupported Question Response

```typescript
export const unsupportedResponse = {
  message: 'This question cannot currently be answered using the available scholarly data.',
  suggestions: [
    'Which authors published in Venue Alpha?',
    'Which venues are associated with Author D?',
    'How many publications were there in 2024?',
    'Who are the most prolific authors?'
  ]
};
```

#### 2i. Prompt Templates

Generated prompt text for common interactions:

```typescript
export const promptTemplates = {
  pivotToVenue: (author: string) =>
    `Which venues has ${author} published in?`,
  pivotToYear: (author: string) =>
    `How has ${author}'s publication output changed over time?`,
  pivotToAuthor: (venue: string) =>
    `Who are the most active authors at ${venue}?`,
  pivotToVenueFromYear: (year: number) =>
    `Which venues had the most publications in ${year}?`,
  sortBy: (facet: string, direction: string) =>
    `Sort ${facet} by publication count ${direction}.`
};
```

#### Export Structure

```typescript
export function getMockData(targetFacet: Facet, filters: Filter[]): {
  rows: FacetRow[];
  observations: Observation[];
  followUps: FollowUpQuestion[];
} {
  // Return appropriate mock data based on target facet and active filters
  // If no filters, return the default dataset for the target facet
  // If filters exist, return filtered/pivoted data
}
```

---

### Step 3: Exploration Store

**File:** `src/lib/stores/exploration.svelte.ts` (CREATE)

Svelte 5 runes-based store managing all exploration state.

```typescript
import { getMockData } from '$lib/data/mock-data';
import type { Facet, Filter, SortState, LoadingStage, ErrorState, GeneratedPrompt, FacetRow, Observation, FollowUpQuestion } from '$lib/types/exploration';

function createExplorationStore() {
  // State
  let input = $state('');
  let targetFacet = $state<Facet | null>(null);
  let filters = $state<Filter[]>([]);
  let sorting = $state<SortState | null>(null);
  let rows = $state<FacetRow[]>([]);
  let observations = $state<Observation[]>([]);
  let followUpQuestions = $state<FollowUpQuestion[]>([]);
  let loadingStage = $state<LoadingStage>(null);
  let error = $state<ErrorState | null>(null);
  let promptOutputMode = $state<'input' | 'tooltip'>('tooltip');
  let generatedPrompt = $state<GeneratedPrompt | null>(null);
  let hasSubmitted = $state(false);

  // Actions

  async function submitQuestion(question: string) {
    if (!question.trim() || loadingStage !== null) return;

    input = question.trim();
    hasSubmitted = true;
    error = null;
    generatedPrompt = null;

    // Simulate loading stages
    loadingStage = 'interpreting';
    await delay(600);

    loadingStage = 'preparing';
    await delay(400);

    loadingStage = 'querying';
    await delay(800);

    loadingStage = 'analyzing';
    await delay(500);

    // Check for unsupported questions (keyword-based)
    if (isUnsupported(question)) {
      loadingStage = null;
      error = {
        type: 'unsupported',
        message: unsupportedResponse.message,
        suggestions: unsupportedResponse.suggestions
      };
      return;
    }

    // Load mock data
    const data = getMockData('author', []);
    targetFacet = 'author';
    filters = [];
    sorting = null;
    rows = data.rows;
    observations = data.observations;
    followUpQuestions = data.followUps;
    loadingStage = null;
  }

  function pivotCell(rowIndex: number, clickedFacet: Facet) {
    if (rows.length === 0) return;

    const row = rows[rowIndex];
    const currentTarget = targetFacet;

    // Add filter for the current target facet value
    const newFilter: Filter = {
      field: currentTarget!,
      operator: '=',
      value: row.targetValue
    };

    // Avoid duplicate filters
    const existingFilterIndex = filters.findIndex(
      f => f.field === newFilter.field && f.value === newFilter.value
    );
    const newFilters = existingFilterIndex >= 0
      ? [...filters]
      : [...filters, newFilter];

    // Update state
    filters = newFilters;
    targetFacet = clickedFacet;

    // Load appropriate mock data
    const data = getMockData(clickedFacet, newFilters);
    rows = data.rows;
    observations = data.observations;
    followUpQuestions = data.followUps;
    sorting = null;

    // Generate prompt
    generatedPrompt = {
      text: generatePromptText(row.targetValue, currentTarget!, clickedFacet),
      targetCell: { rowIndex, facet: clickedFacet }
    };

    // If mode is 'input', populate input
    if (promptOutputMode === 'input') {
      input = generatedPrompt.text;
    }
  }

  function removeFilter(index: number) {
    filters = filters.filter((_, i) => i !== index);

    if (filters.length === 0) {
      // Reset to initial state
      targetFacet = null;
      rows = [];
      observations = [];
      followUpQuestions = [];
    } else {
      // Recompute with remaining filters
      const data = getMockData(targetFacet!, filters);
      rows = data.rows;
      observations = data.observations;
      followUpQuestions = data.followUps;
    }
    sorting = null;
    generatedPrompt = null;
  }

  function sortFacet(facet: Facet) {
    if (sorting && sorting.facet === facet) {
      if (sorting.direction === 'asc') {
        sorting = { facet, direction: 'desc' };
      } else {
        sorting = null; // Reset to unsorted
      }
    } else {
      sorting = { facet, direction: 'asc' };
    }

    // Sort rows
    if (sorting) {
      rows = [...rows].sort((a, b) => {
        const aVal = a.connections[facet] as number;
        const bVal = b.connections[facet] as number;
        return sorting!.direction === 'asc' ? aVal - bVal : bVal - aVal;
      });
    }
  }

  function selectFollowUp(question: string) {
    input = question;
    submitQuestion(question);
  }

  function togglePromptMode() {
    promptOutputMode = promptOutputMode === 'input' ? 'tooltip' : 'input';
    generatedPrompt = null;
  }

  function clearPrompt() {
    generatedPrompt = null;
  }

  function reset() {
    input = '';
    targetFacet = null;
    filters = [];
    sorting = null;
    rows = [];
    observations = [];
    followUpQuestions = [];
    loadingStage = null;
    error = null;
    generatedPrompt = null;
    hasSubmitted = false;
  }

  // Helpers

  function delay(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function isUnsupported(question: string): boolean {
    const lower = question.toLowerCase();
    // Keywords that indicate unsupported queries
    const unsupportedPatterns = [
      'citations',
      'h-index',
      'impact factor',
      'co-author',
      'download',
      'full text'
    ];
    return unsupportedPatterns.some(p => lower.includes(p));
  }

  function generatePromptText(
    filterValue: string | number,
    fromFacet: Facet,
    toFacet: Facet
  ): string {
    if (toFacet === 'venue') return `Which venues has ${filterValue} published in?`;
    if (toFacet === 'year') return `How has ${filterValue}'s publication output changed over time?`;
    if (toFacet === 'author') return `Who are the most active authors at ${filterValue}?`;
    return `Explore ${filterValue} by ${toFacet}`;
  }

  return {
    get input() { return input; },
    set input(v: string) { input = v; },
    get targetFacet() { return targetFacet; },
    get filters() { return filters; },
    get sorting() { return sorting; },
    get rows() { return rows; },
    get observations() { return observations; },
    get followUpQuestions() { return followUpQuestions; },
    get loadingStage() { return loadingStage; },
    get error() { return error; },
    get promptOutputMode() { return promptOutputMode; },
    get generatedPrompt() { return generatedPrompt; },
    get hasSubmitted() { return hasSubmitted; },
    submitQuestion,
    pivotCell,
    removeFilter,
    sortFacet,
    selectFollowUp,
    togglePromptMode,
    clearPrompt,
    reset
  };
}

export const explorationStore = createExplorationStore();
```

---

### Step 4: Design Tokens

**File:** `src/app.css` (MODIFY)

Add the following tokens to the existing `:root` block:

```css
:root {
  /* ... existing tokens ... */

  /* Target facet */
  --target-accent: #0d6efd;
  --target-accent-light: #e7f1ff;
  --target-accent-border: #b6d4fe;

  /* AI observations */
  --observation-bg: #f8f9fa;
  --observation-border: #e9ecef;

  /* Filter pills */
  --filter-bg: #e7f1ff;
  --filter-text: #0d6efd;
  --filter-border: #b6d4fe;

  /* Cell states */
  --cell-hover: #f1f3f5;
  --cell-active: #e7f1ff;
  --cell-disabled-bg: #f8f9fa;
  --cell-disabled-text: #adb5bd;
}
```

---

### Step 5: Components (bottom-up build order)

Build components in dependency order: atoms first, then molecules, then organisms, then page.

---

#### Step 5a: FacetCell Component

**File:** `src/lib/components/FacetCell.svelte` (CREATE)

**Purpose:** A single interactive numeric cell in the facet table.

**Props:**

```typescript
let {
  value,           // number | string - the cell value
  isTarget,        // boolean - is this cell in the target column?
  facet,           // Facet - which facet this cell represents
  disabled,        // boolean - is interaction disabled?
  onActivate,      // () => void - called on click/enter
  onHoverStart,    // () => void - called on mouseenter/focus
  onHoverEnd       // () => void - called on mouseleave/blur
} = $props();
```

**Behavior:**

- If `isTarget` is true: render as a label (non-interactive, normal text)
- If `isTarget` is false and `disabled` is false: render as interactive cell
- Interactive cells have these states:
  - **DEFAULT:** Normal background, pointer cursor on hover
  - **HOVER:** `--cell-hover` background, cursor pointer
  - **FOCUS:** `--accent` ring (2px solid, offset 2px)
  - **ACTIVE:** `--cell-active` background
  - **DISABLED:** `--cell-disabled-bg` background, `--cell-disabled-text` color, no cursor
- Keyboard: Enter or Space triggers `onActivate()`
- Uses `role="button"` and `tabindex="0"` for accessibility
- Hover triggers `onHoverStart()`, leave triggers `onHoverEnd()`

**Style notes:**

- Follow the existing table cell style from `TableResult.svelte`
- Use the existing design tokens from `app.css`
- Keep compact padding (0.5rem 0.75rem)
- Transition on background-color: 0.1s ease

---

#### Step 5b: PromptTooltip Component

**File:** `src/lib/components/PromptTooltip.svelte` (CREATE)

**Purpose:** A floating tooltip that shows a generated natural-language prompt near a hovered cell.

**Props:**

```typescript
let {
  text,            // string - the prompt text to display
  visible,         // boolean - whether to show the tooltip
  position         // { x: number, y: number } - viewport coordinates
} = $props();
```

**Behavior:**

- Uses `position: fixed` to float at the given viewport coordinates
- Renders near the hovered cell, slightly offset (e.g., 8px to the right, centered vertically)
- Max-width: 280px
- Fades in/out with opacity transition (0.15s ease)
- Has a small CSS triangle arrow pointing toward the source cell
- Subtle shadow (`0 2px 8px rgba(0,0,0,0.12)`)
- Small font size (0.8125rem)
- Background: `--bg-elevated`, border: `--border`
- Rounded corners (6px)

**Style:**

```css
.tooltip {
  position: fixed;
  z-index: 50;
  max-width: 280px;
  padding: 0.5rem 0.75rem;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  font-size: 0.8125rem;
  color: var(--text-primary);
  line-height: 1.4;
  opacity: 0;
  transition: opacity 0.15s ease;
  pointer-events: none;
}

.tooltip.visible {
  opacity: 1;
}
```

---

#### Step 5c: ObservationItem Component

**File:** `src/lib/components/ObservationItem.svelte` (CREATE)

**Purpose:** Renders a single observation text.

**Props:**

```typescript
let { text } = $props();
```

**Style:**

- Small left border accent (3px solid `--accent`)
- Background: `--observation-bg`
- Padding: 0.5rem 0.75rem
- Font size: 0.8125rem
- Color: `--text-secondary`
- Border-radius: 4px
- Margin-bottom: 0.5rem

---

#### Step 5d: FollowUpButton Component

**File:** `src/lib/components/FollowUpButton.svelte` (CREATE)

**Purpose:** A clickable button that triggers a follow-up question.

**Props:**

```typescript
let { text, onClick } = $props();
```

**Style:**

- Full-width button
- Background: transparent
- Border: 1px solid `--border`
- Padding: 0.5rem 0.75rem
- Font size: 0.8125rem
- Text-align: left
- Border-radius: 6px
- Cursor: pointer
- Hover: border-color `--accent`, background `--accent-light`
- Focus-visible: `--accent` ring
- Transition: all 0.15s ease

---

#### Step 5e: ActiveFilters Component

**File:** `src/lib/components/ActiveFilters.svelte` (CREATE)

**Purpose:** Renders removable filter pills.

**Props:**

```typescript
let { filters, onRemove } = $props();
// filters: Filter[]
// onRemove: (index: number) => void
```

**Rendered output:**

```
[ Venue = SIGIR x ] [ Year >= 2020 x ]
```

**Style for each pill:**

- Background: `--filter-bg`
- Color: `--filter-text`
- Border: 1px solid `--filter-border`
- Border-radius: 9999px (pill shape)
- Padding: 0.25rem 0.5rem
- Font-size: 0.75rem
- Font-weight: 500
- Display: inline-flex, align-items center, gap 0.375rem
- Remove button: small x icon, hover color `--error`

---

#### Step 5f: FacetToolbar Component

**File:** `src/lib/components/FacetToolbar.svelte` (CREATE)

**Purpose:** Toolbar above the facet table showing target facet, active filters, and sort controls.

**Props:**

```typescript
let {
  targetFacet,      // Facet | null
  filters,          // Filter[]
  sortState,        // SortState | null
  onRemoveFilter,   // (index: number) => void
  onSort            // (facet: Facet) => void
} = $props();
```

**Layout:**

```
[Target: Authors]  [ Venue = Alpha x ] [ Year >= 2020 x ]     [Sort: Publications v]
```

- Left: Target facet badge (accent background, white text, pill shape)
- Center: ActiveFilters component
- Right: Sort control button (cycles UNSORTED -> ASC -> DESC)
- Flexbox, space-between, wrap on mobile

---

#### Step 5g: FacetTable Component

**File:** `src/lib/components/FacetTable.svelte` (CREATE)

**Purpose:** The main faceted search table.

**Props:**

```typescript
let {
  targetFacet,      // Facet | null
  rows,             // FacetRow[]
  sorting,          // SortState | null
  loading,          // boolean
  onCellClick,      // (rowIndex: number, facet: Facet) => void
  onCellHover,      // (rowIndex: number, facet: Facet) => void
  onCellHoverEnd    // () => void
} = $props();
```

**Behavior:**

- If `targetFacet` is null and no rows: show empty state message
- If `loading`: show skeleton placeholder rows (3-5 animated rows)
- Table header: facet labels (Author, Venues, Years, Publications)
  - Sort indicator on the sorted column (arrow up/down)
  - Clickable header to trigger sort
- Target column: visually distinguished
  - Left border: 3px solid `--target-accent`
  - Background: `--target-accent-light`
  - Font-weight: 600
- Non-target columns: rendered via FacetCell
  - Numeric values are interactive
  - Click triggers `onCellClick(rowIndex, facet)`
- Empty state: "Enter a question to begin exploring the scholarly literature."
- Use proper `<table>`, `<thead>`, `<tbody>`, `<th scope="col">`

**Style:**

- Follow existing table style from `TableResult.svelte`
- Border: 1px solid `--border`
- Border-radius: 8px
- Overflow: hidden
- Header: `--bg-secondary` background, small font, semibold
- Rows: subtle dividers, hover highlight
- Target column cell: `--target-accent-light` background

---

#### Step 5h: InsightsPanel Component

**File:** `src/lib/components/InsightsPanel.svelte` (CREATE)

**Purpose:** Displays AI-generated observations and follow-up questions.

**Props:**

```typescript
let {
  observations,         // Observation[]
  followUpQuestions,    // FollowUpQuestion[]
  onFollowUp            // (text: string) => void
} = $props();
```

**Layout:**

```
+------------------------------------+
| AI Observations                    |
+------------------------------------+
| [!] Author A and Author B are...   |
| [!] Publication activity spans...  |
|                                    |
| Suggested Questions                |
|                                    |
| [How has output changed over time?]|
| [Which venues have most pubs?]     |
| [Who are the most prolific?]       |
+------------------------------------+
```

**Style:**

- Background: `--observation-bg`
- Border: 1px solid `--observation-border`
- Border-radius: 8px
- Padding: 1rem
- Header "AI Observations": semibold, small uppercase, muted color
- Visual indicator (icon or badge) that this is AI-generated content
- Observations rendered via ObservationItem
- Divider between observations and questions
- "Suggested Questions" header
- Questions rendered via FollowUpButton
- Empty state: "Observations will appear here after a query."

**Important:** Visually distinguish this panel from the data table (section 23 of requirements). Use a different background color and a subtle "AI" badge.

---

#### Step 5i: LoadingState Component

**File:** `src/lib/components/LoadingState.svelte` (CREATE)

**Purpose:** Shows multi-stage loading progress.

**Props:**

```typescript
let { stage } = $props();
// stage: LoadingStage
```

**Rendered stages:**

| Stage        | Display Text                      |
|-------------|-----------------------------------|
| interpreting | Interpreting question...          |
| preparing    | Preparing search...               |
| querying     | Querying scholarly data...        |
| analyzing    | Analyzing results...              |

**Style:**

- Full-width bar between search panel and results
- Background: `--bg-primary`
- Border: 1px solid `--border`
- Border-radius: 8px
- Padding: 1rem
- Spinner (existing `.spinner` class from app.css)
- Text: `--text-secondary`, 0.875rem
- Animated dots or progress indicator
- `aria-live="polite"` for screen reader announcements

---

#### Step 5j: UnsupportedState Component

**File:** `src/lib/components/UnsupportedState.svelte` (CREATE)

**Purpose:** Shows when a question cannot be answered.

**Props:**

```typescript
let {
  suggestions,          // string[]
  onSuggestionClick     // (text: string) => void
} = $props();
```

**Rendered output:**

```
+--------------------------------------------+
| This question cannot currently be answered  |
| using the available scholarly data.         |
|                                            |
| You could try:                             |
|                                            |
| [Which authors published in ...?]          |
| [Which venues are associated with ...?]    |
+--------------------------------------------+
```

**Style:**

- Background: `--bg-primary`
- Border: 1px solid `--warning`
- Border-radius: 8px
- Padding: 1.25rem
- Warning icon
- Message text: `--text-primary`, 0.875rem
- Suggestions: rendered as FollowUpButton (same style)

---

#### Step 5k: ErrorState Component

**File:** `src/lib/components/ErrorState.svelte` (CREATE)

**Purpose:** Shows technical errors.

**Props:**

```typescript
let {
  error,        // ErrorState
  onRetry       // () => void
} = $props();
```

**Render by type:**

- **generic:** "Something went wrong." + [Try again] button
- **unavailable:** "The scholarly data source is temporarily unavailable." + [Try again] button

**Style:**

- Background: `--bg-primary`
- Border: 1px solid `--error` (generic) or `--warning` (unavailable)
- Border-radius: 8px
- Padding: 1.25rem
- Error/warning icon
- Text: 0.875rem
- Retry button: secondary button style
- `role="alert"` for accessibility

---

#### Step 5l: Header Component

**File:** `src/lib/components/Header.svelte` (CREATE)

**Purpose:** Application header with title and settings.

**Props:**

```typescript
let {
  promptOutputMode,     // 'input' | 'tooltip'
  onToggleMode          // () => void
} = $props();
```

**Layout:**

```
+------------------------------------------------------------------+
| [icon] Scholarly Explorer                    [tooltip/input icon] |
|        LLM-Assisted Exploratory Search                           |
+------------------------------------------------------------------+
```

**Style:**

- Background: `--bg-primary`
- Border-bottom: 1px solid `--border`
- Padding: 0.75rem 1rem
- Title: 1rem, semibold, `--text-primary`
- Subtitle: 0.75rem, `--text-muted`
- Settings button: icon-only, shows current mode, toggles on click
  - Tooltip mode icon: speech bubble with cursor
  - Input mode icon: text field icon
  - `aria-label="Switch prompt output mode"`

---

#### Step 5m: SearchPanel Component

**File:** `src/lib/components/SearchPanel.svelte` (CREATE)

**Purpose:** Natural-language input box.

**Props:**

```typescript
let {
  value,                // string
  disabled,             // boolean
  generatedPrompt,      // string | null
  onSubmit,             // (text: string) => void
  onInput               // (text: string) => void
} = $props();
```

**Behavior:**

- Multiline textarea (auto-resize, max 3 rows)
- Submit button with arrow icon (right side)
- Enter to submit, Shift+Enter for newline
- Disabled while loading
- When `generatedPrompt` arrives and mode is 'input': populate textarea with prompt text, highlight briefly
- Placeholder: "Ask a question about the scholarly literature..."

**States:**

- EMPTY: placeholder text, muted
- USER_TYPING: normal border
- SUBMITTING: disabled, spinner on button
- FOCUSED: accent border + ring

**Style:**

- Follow existing ChatInput style
- Pill shape (border-radius: 24px)
- Leading icon (search/magnifying glass)
- Padding: 0.75rem 1rem
- Max-width: 900px, centered
- Focus-within: accent border + ring

---

#### Step 5n: ExplorationWorkspace Component

**File:** `src/lib/components/ExplorationWorkspace.svelte` (CREATE)

**Purpose:** Two-column layout container for table + insights.

**Props:**

```typescript
let { children } = $props();
```

**Layout:**

- CSS Grid: `grid-template-columns: 1fr 360px`
- Gap: 1rem
- Max-width: 1200px, centered
- Padding: 0 1rem

**Responsive:**

```css
@media (max-width: 768px) {
  .workspace {
    grid-template-columns: 1fr;
  }
}
```

**Children:** FacetToolbar + FacetTable (left), InsightsPanel (right)

---

### Step 6: Page Layout

**File:** `src/routes/+page.svelte` (MODIFY)

Replace the entire chat-based layout with the new exploratory search UI.

**Structure:**

```svelte
<script>
  import Header from '$lib/components/Header.svelte';
  import SearchPanel from '$lib/components/SearchPanel.svelte';
  import ExplorationWorkspace from '$lib/components/ExplorationWorkspace.svelte';
  import FacetToolbar from '$lib/components/FacetToolbar.svelte';
  import FacetTable from '$lib/components/FacetTable.svelte';
  import InsightsPanel from '$lib/components/InsightsPanel.svelte';
  import LoadingState from '$lib/components/LoadingState.svelte';
  import UnsupportedState from '$lib/components/UnsupportedState.svelte';
  import ErrorState from '$lib/components/ErrorState.svelte';
  import PromptTooltip from '$lib/components/PromptTooltip.svelte';
  import { explorationStore } from '$lib/stores/exploration.svelte';
</script>

<svelte:head>
  <title>Scholarly Explorer</title>
  <meta name="description" content="LLM-Assisted Exploratory Search in Scholarly Knowledge Graphs" />
</svelte:head>

<div class="app">
  <Header
    promptOutputMode={explorationStore.promptOutputMode}
    onToggleMode={() => explorationStore.togglePromptMode()}
  />

  <SearchPanel
    value={explorationStore.input}
    disabled={explorationStore.loadingStage !== null}
    generatedPrompt={explorationStore.generatedPrompt?.text ?? null}
    onSubmit={(text) => explorationStore.submitQuestion(text)}
    onInput={(text) => { explorationStore.input = text; }}
  />

  {#if explorationStore.loadingStage}
    <LoadingState stage={explorationStore.loadingStage} />
  {/if}

  {#if explorationStore.error}
    {#if explorationStore.error.type === 'unsupported'}
      <UnsupportedState
        suggestions={explorationStore.error.suggestions ?? []}
        onSuggestionClick={(text) => explorationStore.selectFollowUp(text)}
      />
    {:else}
      <ErrorState
        error={explorationStore.error}
        onRetry={() => explorationStore.submitQuestion(explorationStore.input)}
      />
    {/if}
  {/if}

  {#if explorationStore.hasSubmitted && !explorationStore.loadingStage && !explorationStore.error}
    <ExplorationWorkspace>
      {#snippet left()}
        <FacetToolbar
          targetFacet={explorationStore.targetFacet}
          filters={explorationStore.filters}
          sortState={explorationStore.sorting}
          onRemoveFilter={(i) => explorationStore.removeFilter(i)}
          onSort={(facet) => explorationStore.sortFacet(facet)}
        />
        <FacetTable
          targetFacet={explorationStore.targetFacet}
          rows={explorationStore.rows}
          sorting={explorationStore.sorting}
          loading={false}
          onCellClick={(rowIdx, facet) => explorationStore.pivotCell(rowIdx, facet)}
          onCellHover={(rowIdx, facet) => explorationStore.generatePrompt(rowIdx, facet)}
          onCellHoverEnd={() => explorationStore.clearPrompt()}
        />
      {/snippet}

      {#snippet right()}
        <InsightsPanel
          observations={explorationStore.observations}
          followUpQuestions={explorationStore.followUpQuestions}
          onFollowUp={(text) => explorationStore.selectFollowUp(text)}
        />
      {/snippet}
    </ExplorationWorkspace>
  {/if}

  {#if !explorationStore.hasSubmitted}
    <!-- Welcome/empty state -->
    <div class="welcome">
      <h2>Welcome to Scholarly Explorer</h2>
      <p>Ask a question about the scholarly literature to begin exploring.</p>
      <div class="examples">
        <p class="example-title">Try asking:</p>
        <ul>
          <li onclick={() => explorationStore.submitQuestion('Who are the most prolific authors?')}>
            "Who are the most prolific authors?"
          </li>
          <li onclick={() => explorationStore.submitQuestion('Which venues have the most publications?')}>
            "Which venues have the most publications?"
          </li>
          <li onclick={() => explorationStore.submitQuestion('How has publication output changed over time?')}>
            "How has publication output changed over time?"
          </li>
        </ul>
      </div>
    </div>
  {/if}

  {#if explorationStore.promptOutputMode === 'tooltip' && explorationStore.generatedPrompt}
    <PromptTooltip
      text={explorationStore.generatedPrompt.text}
      visible={true}
      position={{ x: 0, y: 0 }}  <!-- Position managed by FacetCell -->
    />
  {/if}
</div>
```

**Note on ExplorationWorkspace:** The workspace component needs to accept named snippets for left/right panels. Alternatively, use props or slots. The exact pattern depends on Svelte 5 snippet support. If snippets don't work for this layout, use direct children with conditional rendering inside the workspace component.

**Note on PromptTooltip positioning:** The tooltip position should be calculated in the FacetCell component and passed up via the store or a callback. The FacetCell's `onHoverStart` should capture the cell's bounding rect and store the position. The PromptTooltip reads this position from the store.

---

### Step 7: Update API Client

**File:** `src/lib/api/client.ts` (MODIFY)

Add mock exploration functions. Keep the existing `sendChatMessage` function commented out or remove it entirely.

```typescript
// Mock exploration functions (no backend needed)

export async function exploreQuestion(question: string): Promise<ExplorationResult> {
  await new Promise(r => setTimeout(r, 2300)); // Simulate LLM + DBLP latency
  return mockExploreResult(question);
}

export async function tableInteraction(interaction: InteractionRequest): Promise<InteractionResult> {
  await new Promise(r => setTimeout(r, 300)); // Simulate quick pivot
  return mockInteractionResult(interaction);
}
```

These functions are not actually used by the store (which uses `getMockData` directly), but they establish the API contract for future backend integration.

---

### Step 8: Delete Old Files

Delete the following files that are no longer needed:

- `src/lib/components/ChatHeader.svelte`
- `src/lib/components/ChatInput.svelte`
- `src/lib/components/ChatMessage.svelte`
- `src/lib/components/SparqlCodeBlock.svelte`
- `src/lib/components/TableResult.svelte`
- `src/lib/stores/chat.svelte.ts`

---

## Component Dependency Graph

Build in this order (each component only depends on components above it):

```
1. Types (exploration.ts)
2. Mock Data (mock-data.ts)
3. Store (exploration.svelte.ts)
4. Design Tokens (app.css)
5. FacetCell
6. PromptTooltip
7. ObservationItem
8. FollowUpButton
9. ActiveFilters
10. FacetToolbar (depends on ActiveFilters)
11. FacetTable (depends on FacetCell)
12. InsightsPanel (depends on ObservationItem, FollowUpButton)
13. LoadingState
14. UnsupportedState (depends on FollowUpButton)
15. ErrorState
16. Header
17. SearchPanel
18. ExplorationWorkspace
19. +page.svelte (depends on everything)
20. Delete old files
```

---

## Interaction Flows

### Flow A: Submit Question

```
User types "Who are the most prolific authors?"
  -> SearchPanel.onSubmit("Who are the most prolific authors?")
  -> explorationStore.submitQuestion("Who are the most prolific authors?")
  -> loadingStage = 'interpreting' (600ms)
  -> loadingStage = 'preparing' (400ms)
  -> loadingStage = 'querying' (800ms)
  -> loadingStage = 'analyzing' (500ms)
  -> Load mock data: targetFacet='author', rows=[...], observations=[...], followUps=[...]
  -> loadingStage = null
  -> Render: FacetToolbar + FacetTable + InsightsPanel
```

### Flow B: Pivot (Cell Click)

```
User clicks "12" in Author A row, Venues column
  -> FacetCell.onActivate()
  -> explorationStore.pivotCell(0, 'venue')
  -> Add filter: { field: 'author', operator: '=', value: 'Author A' }
  -> Set targetFacet = 'venue'
  -> Load mock data: filtered venues for Author A
  -> Generate prompt: "Which venues has Author A published in?"
  -> If mode='tooltip': show PromptTooltip near cell
  -> If mode='input': populate SearchPanel with prompt
  -> Render: updated table + updated insights
```

### Flow C: Follow-up Question

```
User clicks "How has publication output changed over time?"
  -> FollowUpButton.onClick()
  -> explorationStore.selectFollowUp("How has publication output changed over time?")
  -> Set input = question
  -> Trigger submitQuestion() (same as Flow A)
```

### Flow D: Remove Filter

```
User clicks "x" on "Author A" filter pill
  -> ActiveFilters.onRemove(0)
  -> explorationStore.removeFilter(0)
  -> If no filters remain: reset to initial state
  -> If filters remain: recompute with remaining filters
  -> Render: updated table
```

### Flow E: Sort

```
User clicks "Publications" header or sort button
  -> explorationStore.sortFacet('publication')
  -> If no sort: set asc
  -> If asc: set desc
  -> If desc: clear sort
  -> Sort rows array
  -> Render: reordered table rows
```

### Flow F: Unsupported Question

```
User asks "What is the h-index of Author A?"
  -> submitQuestion() detects 'h-index' keyword
  -> Set error = { type: 'unsupported', message: '...', suggestions: [...] }
  -> loadingStage = null
  -> Render: UnsupportedState with suggestion buttons
```

---

## Responsive Breakpoints

| Breakpoint | Layout |
|------------|--------|
| > 1024px   | Two-column grid (table fluid, insights 360px) |
| 768-1024px | Two-column grid (table fluid, insights 300px) |
| < 768px    | Single column stack (search -> table -> insights) |

**Mobile-specific:**

- FacetToolbar: wrap filters vertically
- FacetTable: horizontal scroll for wide tables
- InsightsPanel: full width below table
- SearchPanel: full width, smaller padding
- Header: compact, subtitle hidden

---

## Accessibility Checklist

- [ ] All interactive cells: `role="button"`, `tabindex="0"`, Enter/Space activation
- [ ] Focus-visible: accent ring on all interactive elements
- [ ] Filter pills: `aria-label="Remove filter: Venue = SIGIR"`
- [ ] Loading state: `aria-live="polite"` for stage announcements
- [ ] Error state: `role="alert"`
- [ ] Table: proper `<th>` with `scope="col"`
- [ ] Tooltip: `role="tooltip"`, `aria-describedby` on source cell
- [ ] Follow-up buttons: descriptive `aria-label`
- [ ] Settings toggle: `aria-pressed` state
- [ ] Screen reader: announce table updates
- [ ] Keyboard: tab navigation through all interactive elements
- [ ] Color: never encode meaning only through color

---

## Design System Compliance

Follow these rules from the ui-design-system skill:

- **Colors:** Reuse existing CSS custom properties from `app.css`. No arbitrary colors.
- **Typography:** Page title large+bold, section headings medium+semibold, body regular, metadata small+muted.
- **Spacing:** Use consistent spacing (0.25rem, 0.5rem, 0.75rem, 1rem, 1.5rem).
- **Borders:** Light borders for containers, stronger for inputs, accent for focus.
- **Buttons:** Primary for main actions, secondary for supporting, icon-only only when meaning is clear.
- **Tables:** Dense, structured, readable. Muted header, subtle dividers, hover states.
- **Interaction states:** Every interactive element needs default, hover, focus, active, disabled states.
- **No decoration:** No excessive gradients, shadows, rounded corners, or animation.
- **Consistency:** One visual system for all buttons, inputs, cards, badges, tables.

---

## Summary

| Action | Count | Files |
|--------|-------|-------|
| CREATE | 17    | exploration.ts, mock-data.ts, exploration.svelte.ts, Header.svelte, SearchPanel.svelte, ExplorationWorkspace.svelte, FacetToolbar.svelte, ActiveFilters.svelte, FacetTable.svelte, FacetCell.svelte, InsightsPanel.svelte, ObservationItem.svelte, FollowUpButton.svelte, PromptTooltip.svelte, LoadingState.svelte, UnsupportedState.svelte, ErrorState.svelte |
| MODIFY | 3     | +page.svelte, app.css, client.ts |
| DELETE | 6     | ChatHeader.svelte, ChatInput.svelte, ChatMessage.svelte, SparqlCodeBlock.svelte, TableResult.svelte, chat.svelte.ts |

**Total: 26 file operations**

---

## Definition of Done

The implementation is complete when a user can:

1. See the welcome screen with example questions
2. Type a natural-language question and submit it
3. See multi-stage loading progress
4. See the faceted table with a target facet column highlighted
5. See numeric connection cells in non-target columns
6. Hover over a numeric cell and see a tooltip with a generated prompt
7. Click a numeric cell to pivot the table (add filter + change target)
8. See active filter pills above the table
9. Remove a filter by clicking the x on a pill
10. Sort results by clicking a column header or sort control
11. See AI observations in the insights panel
12. Click a follow-up question to populate the search and trigger a new query
13. See an explicit unsupported question message with suggestions
14. See distinct error states for technical errors vs. unsupported questions
15. Distinguish data (table) from AI interpretation (observations)
16. Use all features via keyboard only
17. See a responsive layout on mobile (stacked)
