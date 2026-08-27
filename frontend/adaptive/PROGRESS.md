# Project Progress

## Goal

Build and iterate on an adaptive conversational knowledge graph explorer frontend application (`frontend/adaptive/`) using SvelteKit, Tailwind CSS, and TypeScript. The app allows users to explore scholarly publications through natural language queries, with the UI adapting dynamically based on conversation context. The project uses mock data and follows specific commit conventions (`feat(frontend/adaptive):`, `fix(frontend/adaptive):`, etc.).

## Instructions

- Follow traceable monorepo commit conventions: `feat(frontend/adaptive):`, `fix(frontend/adaptive):`, `refactor(frontend/adaptive):`, `docs(frontend/adaptive):`, `style(frontend/adaptive):`
- Run `npm run check` before committing to verify 0 errors, 0 warnings
- Use `git push origin feat/exploratory-search-ui` to push changes
- The UI design system emphasizes clean, restrained, professional design with consistent spacing, typography, and color tokens defined in `app.css`
- The app has two response modes: **answerable** (natural language + result table + observations + suggestions) and **unsupported** (natural language + suggestions only)
- The ResultBox has two tabs: "Sparql Query" (left) and "Result Table" (right), defaulting to SPARQL view
- All data views use a single type: `facet_table` (sortable table)
- `BACKEND-API-GUIDE.md` documents the API contract for backend developers
- `TEST-PLAN.md` and `TEST-REPORT.md` document testing

## Discoveries

1. **Per-turn data storage is essential** — Single `result`/`observations`/`suggestions` variables got overwritten on each new message, losing previous response data. Fixed by adding per-turn Maps (`resultsByTurn`, `observationsByTurn`, `suggestionsByTurn`, `filtersByTurn`, `sparqlByTurn`, `statusByTurn`).

2. **WCAG AA contrast** — `--text-muted: #adb5bd` had ~3:1 ratio (fails AA). Changed to `#6c757d` (~5:1).

3. **Session persistence needs Map ↔ Record conversion** — `JSON.stringify` doesn't handle `Map` objects. Used `Object.fromEntries()` for serialization and `new Map(Object.entries())` for deserialization.

4. **ConversationTurn.svelte was never created** — Functionality merged into ConversationView.

5. **Svelte 5 runes only** — `$state`, `$derived`, `$effect`, `$props`. No legacy `$:` or `export let`.

6. **Stale LSP errors** — Some `sparqlByTurn`/`statusByTurn` errors in `+page.svelte` are LSP cache issues; `npm run check` confirms 0 errors.

## Accomplished

### Completed:
- **Phase 0-8**: Full SvelteKit scaffolding, design tokens, types, mock data, store, all components, main page wiring
- **Phase 9**: Session persistence with `persistence.ts` (sessionStorage + URL state)
- **Phase 10**: Keyboard navigation (arrow keys, Home/End, Escape on tables)
- **Phase 11**: Accessibility (aria-live, ARIA labels, focus visibility)
- **BUG-002 fixed**: Muted text contrast for WCAG AA
- **BUG-001**: Test plan typo (won't fix — product behaves correctly)
- **SPARQL query view**: Added `sparql_query` field to types, mock data, store (`sparqlByTurn`), and `BACKEND-API-GUIDE.md`
- **QueryToggle → SparqlBlock + ResultBox**: Extracted SPARQL display, created unified ResultBox with tabs
- **ResultBox redesign**: Two tabs ("Sparql Query" / "Result Table"), default to SPARQL, right-aligned toggle
- **ObservationCard simplified**: Removed AI badge/label, now plain paragraph
- **SuggestionChips simplified**: Removed "You could explore:" label
- **Chat container**: 900px max-width centered, header inside container
- **Title headers removed**: From FacetTable, ComparisonView, TimelineView
- **Two-view system**: Answerable = table + observations + suggestions; Unsupported = text + suggestions only
- **Single data view type**: Simplified `ResultType` to `'facet_table'` only, removed ComparisonView, TimelineView, SummaryView
- **Mock data updated**: All responses use `facet_table` type, unsupported cleaned up
- **Paragraph spacing**: `.query-text` with `margin-bottom: 0.75rem`, observation with `margin-top: 0.625rem`

### Remaining / Future:
- **Planning mode files** (`PLAN.md`, `TEST-PLAN.md`, `TEST-REPORT.md`, `BACKEND-API-GUIDE.md`) may need updates to reflect all the simplifications
- **Backend integration** — currently all mock data
- **P1 features**: Multiple result representations, comparison views, recoverable state
- **P2 features**: Branching exploration paths, saved explorations, collaboration

## Relevant files / directories

```
frontend/adaptive/
├── src/
│   ├── app.css                          — Design tokens, global styles
│   ├── app.html                         — SvelteKit shell
│   ├── app.d.ts                         — TypeScript declarations
│   ├── routes/
│   │   ├── +layout.svelte               — Root layout with app.css import
│   │   └── +page.svelte                 — Main page wiring (store → ConversationView → PromptInput)
│   └── lib/
│       ├── types/
│       │   └── exploration.ts           — All types (ResultType = 'facet_table' only)
│       ├── data/
│       │   ├── mock-responses.ts        — 7 mock scenarios with SPARQL queries
│       │   └── mock-entities.ts         — Sample entities
│       ├── stores/
│       │   └── exploration.svelte.ts    — Main store with per-turn Maps
│       ├── utils/
│       │   └── persistence.ts           — Session storage + URL state
│       └── components/
│           ├── Conversation/
│           │   ├── ConversationView.svelte    — Routes turns, passes per-turn data
│           │   ├── UserMessage.svelte         — User bubble
│           │   └── AssistantMessage.svelte    — Assistant bubble with conditional rendering
│           ├── Results/
│           │   ├── ResultBox.svelte           — Tabs container (SPARQL/Result)
│           │   ├── FacetTable.svelte          — Single data view (sortable table)
│           │   ├── ExplorationRenderer.svelte — Routes to FacetTable only
│           │   └── SparqlBlock.svelte         — SPARQL formatting + copy
│           ├── Insights/
│           │   ├── ObservationCard.svelte     — Plain paragraph (no badge)
│           │   └── SuggestionChips.svelte     — Follow-up suggestion buttons
│           ├── Input/
│           │   └── PromptInput.svelte         — Auto-resize textarea
│           └── Shared/
│               ├── Badge.svelte
│               ├── Spinner.svelte
│               ├── EmptyState.svelte
│               └── ErrorState.svelte
├── static/favicon.svg
├── package.json
├── svelte.config.js
├── vite.config.ts
├── tsconfig.json
├── PLAN.md                              — Full development plan
├── TEST-PLAN.md                         — 65 test cases
├── TEST-REPORT.md                       — Test results (96.9% pass)
└── BACKEND-API-GUIDE.md                 — API contract for backend team

Repository root:
├── BACKEND-API-GUIDE.md                 — Backend API guide
└── README.md
```

### Key file summaries:
- **`+page.svelte`**: Wires store → ConversationView, passes `resultsByTurn`, `observationsByTurn`, `suggestionsByTurn`, `sparqlByTurn`, `statusByTurn`
- **`AssistantMessage.svelte`**: Conditionally renders ResultBox only when `status === 'answerable'`
- **`ResultBox.svelte`**: Two tabs ("Sparql Query" / "Result Table"), defaults to SPARQL, wraps ExplorationRenderer + SparqlBlock
- **`exploration.svelte.ts`**: All per-turn Maps, `sendMessage()`, `saveState()`/`loadState()`, mock response matching
