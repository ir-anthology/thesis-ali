# UI Testing Plan: Scholarly Explorer

**Application:** Adaptive Conversational Knowledge Graph Explorer
**URL:** `http://localhost:5173`
**Testing Type:** Black-box UI testing (no code review required)
**Date:** August 2026

---

## 1. Test Environment Setup

### Prerequisites
- Modern browser (Chrome, Firefox, Safari, Edge - latest versions)
- Screen resolution: 1920x1080 (desktop) and 375x812 (mobile)
- Clear browser cache and sessionStorage before each test suite

### How to Start the Application
```bash
cd frontend/adaptive
npm install
npm run dev
```
Open `http://localhost:5173` in browser.

---

## 2. Test Scenarios

### SUITE 1: Initial State & Welcome Screen

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| TC-001 | Welcome screen displays on first visit | 1. Open the application in a new incognito/private window | - Header shows "Scholarly Explorer" | |
| | | | - Center shows chat icon and "Welcome to Scholarly Explorer" title | |
| | | | - Description text: "Ask me about authors, venues, and publications in the knowledge graph." | |
| | | | - "Try asking:" section with 3 example questions | |
| | | | - Input field at bottom with placeholder "Ask about scholarly publications..." | |
| | | | - Hint text: "Press Enter to send, Shift + Enter for new line" | |
| TC-002 | Header elements | 1. Check header bar | - Title "Scholarly Explorer" on the left | |
| | | | - No "New Exploration" button visible (conversation is empty) | |
| TC-003 | Input field is enabled | 1. Check input field state | - Input field is enabled and focusable | |
| | | | - Send button is visible but disabled (grayed out) | |

---

### SUITE 2: Conversation Input

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| TC-010 | Send message with Enter key | 1. Click input field | Input field gains focus with blue border | |
| | | 2. Type "Who are the most prolific authors?" | Text appears in input field | |
| | | 3. Press Enter | - Input field clears | |
| | | | - User message bubble appears on right side | |
| | | | - Assistant "thinking" indicator appears | |
| TC-011 | Send message with button click | 1. Type a message | Send button becomes enabled (blue) | |
| | | 2. Click the send button | Message is sent, input clears | |
| TC-012 | Shift+Enter for new line | 1. Type "Line 1" | |
| | | 2. Press Shift+Enter | Cursor moves to new line (no message sent) | |
| | | 3. Type "Line 2" | Both lines visible in input | |
| | | 4. Press Enter | Message with both lines is sent | |
| TC-013 | Cannot send empty message | 1. Leave input empty | Send button remains disabled | |
| TC-014 | Cannot send whitespace only | 1. Type "   " (spaces only) | Send button remains disabled | |
| TC-015 | Input auto-resizes | 1. Type a long message (100+ characters) | Input field grows in height (up to max) | |
| | | 2. Send the message | Input field shrinks back to single line | |

---

### SUITE 3: Mock Response Scenarios

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| TC-020 | Prolific authors query | "Who are the most prolific authors?" | - Assistant message: "Most Prolific Authors in Exploratory Search" | |
| | | | - Table with columns: Author, Publications, Venues, Years | |
| | | | - 5 rows of author data | |
| | | | - AI Observation box below table | |
| | | | - 3 suggestion chips | |
| TC-021 | Filter by years | "Only consider the last five years" | - Filter pill appears: "year: 2020–2025 ×" | |
| | | | - Table updates with filtered data | |
| | | | - Title changes to "Most Prolific Authors (2020–2025)" | |
| TC-022 | Venue pivot query | "Which venues do they publish in?" | - Table changes to venue-focused | |
| | | | - Columns: Venue, Publications, Authors, Years | |
| | | | - Data shows SIGIR, CHIIR, CHI, UIST, JASIST | |
| TC-023 | Timeline query | "Show me how this changed over time" | - Bar chart visualization appears | |
| | | | - Years on left, bars for SIGIR, CHIIR, CHI | |
| | | | - Legend shows venue colors | |
| TC-024 | Comparison query | "Compare SIGIR and CHIIR" | - Comparison table with side-by-side data | |
| | | | - Metrics: Total Publications, Authors, Years Active, Avg, Growth | |
| TC-025 | Why question | "Why is SIGIR prominent?" | - Summary view (no table) | |
| | | | - Multiple AI observations explaining SIGIR | |
| TC-026 | Unsupported question | "What is the weather today?" | - Message: "I cannot answer that question..." | |
| | | | - 3 alternative suggestion chips appear | |
| TC-027 | Case insensitivity | "WHO ARE THE MOST PROLICT AUTHORS" | - Same response as TC-020 (matching is case-insensitive) | |

---

### SUITE 4: Table Interactions

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| TC-030 | Column sorting - click | 1. Send "Who are the most prolific authors?" | |
| | | 2. Click "Publications" column header | - Arrow indicator appears (↑ ascending) | |
| | | | - Rows reorder by publication count | |
| | | 3. Click "Publications" header again | - Arrow changes to ↓ (descending) | |
| | | | - Rows reverse order | |
| TC-031 | Sort by different columns | 1. Click "Author" header | - Sort by author name alphabetically | |
| | | 2. Click "Venues" header | - Sort by venue count | |
| TC-032 | Table header hover state | 1. Hover over sortable column header | - Header background changes (subtle highlight) | |
| | | | - Cursor changes to pointer | |
| TC-033 | Table row hover state | 1. Hover over a table row | - Row background changes subtly | |
| TC-034 | Keyboard navigation - Tab | 1. Press Tab key repeatedly | - Focus moves through interactive elements | |
| | | | - Focus indicator (blue outline) visible | |
| TC-035 | Keyboard navigation - Arrow keys | 1. Click on a table row to focus it | |
| | | 2. Press Arrow Down | - Focus moves to next row | |
| | | 3. Press Arrow Up | - Focus moves to previous row | |
| | | 4. Press Home | - Focus moves to first row | |
| | | 5. Press End | - Focus moves to last row | |
| | | 6. Press Escape | - Focus leaves the table | |

---

### SUITE 5: Filter & Pill Interactions

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| TC-040 | Filter pill appears | 1. Send "Only consider the last five years" | - Blue pill appears: "year: 2020–2025 ×" | |
| TC-041 | Remove filter with × | 1. Apply a filter (TC-040) | |
| | | 2. Click the × on the filter pill | - Pill disappears | |
| | | | - Results may update (no filter applied) | |
| TC-042 | Multiple filters | 1. (Note: Current mock only supports one filter at a time) | Verify only one filter pill shows | |
| TC-043 | Filter persists in conversation | 1. Apply filter, then send another message | - Filter pill remains visible | |
| | | | - Filter is part of the conversation context | |

---

### SUITE 6: AI Observations & Suggestions

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| TC-050 | Observation card displays | 1. Send any query that returns results | - Blue-tinted box appears below table | |
| | | | - "AI" badge (blue pill) in top-left | |
| | | | - "INTERPRETATION" label | |
| | | | - Observation text below | |
| TC-051 | Observation has left border | 1. Check observation card styling | - 3px left border (blue) | |
| | | | - Light blue background | |
| TC-052 | Suggestion chips display | 1. Send any query | - "You could explore:" label | |
| | | | - 3 pill-shaped buttons with suggestion text | |
| TC-053 | Click suggestion chip | 1. Click a suggestion chip | - Chip text is sent as new message | |
| | | | - New conversation turn appears | |
| | | | - New results appear | |
| TC-054 | Suggestion chip hover | 1. Hover over suggestion chip | - Background changes to light blue | |
| | | | - Border changes to accent color | |

---

### SUITE 7: Conversation History

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| TC-060 | User message styling | 1. Send a message | - Message appears on RIGHT side | |
| | | | - Blue background bubble | |
| | | | - User avatar (person icon) on right | |
| | | | - "You" label + timestamp | |
| TC-061 | Assistant message styling | 1. Wait for response | - Message appears on LEFT side | |
| | | | - Gray/light background bubble | |
| | | | - Chat icon avatar on left | |
| | | | - "Assistant" label + timestamp | |
| TC-062 | Auto-scroll on new message | 1. Send multiple messages | - Conversation auto-scrolls to bottom | |
| TC-063 | Conversation maintains context | 1. Send "Who are the most prolific authors?" | |
| | | 2. Send "Only consider the last five years" | - Both messages visible in history | |
| | | | - Previous results remain visible (scrolled up) | |
| TC-064 | Loading state | 1. Send a message | - "Thinking about the question..." with spinner appears | |
| | | | - Spinner animates (rotating) | |
| | | | - Input is disabled during loading | |

---

### SUITE 8: Session Persistence

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| TC-070 | State persists on page refresh | 1. Send a message and get response | |
| | | 2. Press F5 (refresh) | - Conversation history is restored | |
| | | | - Results are visible | |
| | | | - Filters (if any) are restored | |
| TC-071 | Clear exploration | 1. Have an active conversation | |
| | | 2. Click "New Exploration" button | - Conversation clears | |
| | | | - Welcome screen reappears | |
| | | | - Session storage is cleared | |
| TC-072 | New Exploration button visibility | 1. Start with empty conversation | - "New Exploration" button is NOT visible | |
| | | 2. Send a message | - "New Exploration" button appears | |

---

### SUITE 9: URL State

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| TC-080 | URL with query parameter | 1. Open `http://localhost:5173/?q=Who+are+the+most+prolific+authors` | - Message is automatically sent | |
| | | | - Results appear without manual input | |

---

### SUITE 10: Responsive Design

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| TC-090 | Desktop layout (1920x1080) | 1. Open at full desktop width | - Header spans full width | |
| | | | - Conversation area fills available space | |
| | | | - Input at bottom | |
| | | | - Table scrolls horizontally if needed | |
| TC-091 | Tablet layout (768px) | 1. Resize browser to 768px width | - Layout adapts, no horizontal overflow | |
| | | | - Table remains readable | |
| | | | - Input remains usable | |
| TC-092 | Mobile layout (375px) | 1. Resize browser to 375px width | - Single column layout | |
| | | | - Messages take full width | |
| | | | - Table scrolls horizontally | |
| | | | - Input field remains accessible | |
| TC-093 | Viewport height changes | 1. Resize browser height | - Layout adjusts without breaking | |
| | | | - Conversation area uses available height | |

---

### SUITE 11: Accessibility

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| TC-100 | Keyboard-only navigation | 1. Use only keyboard (no mouse) | - Can Tab to input field | |
| | | | - Can Tab to send button | |
| | | | - Can Tab to suggestion chips | |
| | | | - Can Tab to filter remove buttons | |
| | | | - Focus indicator visible on all focused elements | |
| TC-101 | Screen reader labels | 1. Use screen reader (NVDA/VoiceOver) | - "Conversation history" region announced | |
| | | | - Send button has accessible label | |
| | | | - Suggestion chips have accessible names | |
| | | | - Filter pills have "Remove filter" labels | |
| TC-102 | Focus visibility | 1. Tab through all interactive elements | - Blue outline ring on all focused elements | |
| | | | - No elements have hidden focus indicators | |
| TC-103 | Color contrast | 1. Check text readability | - All text meets WCAG AA contrast ratio | |
| | | | - Interactive elements distinguishable | |

---

### SUITE 12: Visual Design Compliance

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| TC-110 | Typography hierarchy | 1. Check all text elements | - Page title: large + bold | |
| | | | - Section headings: medium + semibold | |
| | | | - Body text: regular weight | |
| | | | - Metadata (timestamps, labels): small + muted | |
| TC-111 | Color consistency | 1. Check all colored elements | - Accent color used consistently (links, buttons) | |
| | | | - No arbitrary colors | |
| | | | - Error messages in red | |
| | | | - Success states in green | |
| TC-112 | Spacing consistency | 1. Check padding/margins | - Consistent spacing between elements | |
| | | | - Related items closer, unrelated items farther | |
| TC-113 | Border radius | 1. Check rounded elements | - Inputs/buttons: small radius (6px) | |
| | | | - Cards/tables: medium radius (6px) | |
| | | | - Pills/badges: full radius (9999px) | |

---

## 3. Bug Report Template

When filing bugs, use this format:

```
**Bug ID:** BUG-XXX
**Test Case:** TC-XXX
**Severity:** Critical / High / Medium / Low
**Browser:** Chrome/Firefox/Safari/Edge + version
**Resolution:** 1920x1080 / 375x812

**Steps to Reproduce:**
1. ...
2. ...
3. ...

**Expected Result:**
What should happen

**Actual Result:**
What actually happened

**Screenshots/Videos:**
[Attach evidence]

**Additional Notes:**
Any other relevant information
```

---

## 4. Known Limitations to Note

These are **not bugs** but expected behavior based on the mock implementation:

1. **Only 7 query types are recognized** - Other questions get "unsupported" response
2. **Filters are mock-driven** - Clicking filter × removes visual pill but doesn't re-query
3. **No real backend** - All data is from mock responses
4. **URL state only reads `q` parameter** - facet/filters in URL are decoded but not applied
5. **Session storage is browser-tab specific** - Different tabs have separate sessions

---

## 5. Test Execution Checklist

Before signing off, ensure:

- [ ] All TC-0XX tests executed
- [ ] All browsers tested (Chrome, Firefox, Safari, Edge)
- [ ] Both desktop and mobile viewports tested
- [ ] Keyboard navigation verified
- [ ] Screen reader tested (at least one)
- [ ] All bugs filed with severity
- [ ] Screenshots attached for any visual issues

---

## 6. Priority Matrix

**Must Pass (P0):**
- TC-001 to TC-003 (Welcome screen)
- TC-010 to TC-012 (Basic input)
- TC-020 to TC-026 (Core mock responses)
- TC-060 to TC-064 (Conversation display)
- TC-070 to TC-072 (Session persistence)
- TC-090 (Desktop layout)

**Should Pass (P1):**
- TC-030 to TC-035 (Table interactions)
- TC-040 to TC-043 (Filters)
- TC-050 to TC-054 (Observations/Suggestions)
- TC-091 to TC-093 (Responsive)
- TC-100 to TC-103 (Accessibility)

**Nice to Have (P2):**
- TC-080 (URL state)
- TC-110 to TC-113 (Visual design)
