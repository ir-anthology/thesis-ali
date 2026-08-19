# UI Test Plan: Scholarly Explorer

## Scope

Test the exploratory search UI built with SvelteKit 5 + Tailwind CSS 4. All data is mock/hardcoded. No backend integration.

**Dev server:** `npm run dev` (default `http://localhost:5173`)

---

## 1. Application Shell & Header

### TC-1.1: Page loads correctly
- Navigate to `/`
- Verify title in browser tab: "Scholarly Explorer"
- Verify meta description is present

### TC-1.2: Header renders
- Verify header is visible at the top
- Verify logo icon (globe) is visible
- Verify title text: "Scholarly Explorer"
- Verify subtitle text: "LLM-Assisted Exploratory Search in Scholarly Knowledge Graphs"

### TC-1.3: Settings button exists and toggles
- Verify settings button is visible in the top-right
- Hover over settings button: tooltip shows "Prompt output: Tooltip"
- Click settings button: icon changes from chat bubble to document icon
- Hover again: tooltip shows "Prompt output: Input box"
- Click again: icon reverts to chat bubble
- Verify `aria-pressed` attribute toggles between `true` and `false`

### TC-1.4: Header is sticky
- Scroll the main content area down
- Verify header remains fixed at the top

### TC-1.5: Header responsive (mobile)
- Resize viewport to 375px width
- Verify subtitle is hidden
- Verify header layout doesn't break

---

## 2. Search Panel

### TC-2.1: Initial state
- Verify search input is visible with placeholder: "Ask a question about the scholarly literature..."
- Verify search icon (magnifying glass) is visible inside the input
- Verify submit button (arrow) is visible and disabled
- Verify hint text: "Press Enter to send, Shift + Enter for new line"

### TC-2.2: Input focus state
- Click on the textarea
- Verify the wrapper border changes to accent color (blue)
- Verify a blue ring/box-shadow appears around the input
- Click elsewhere: verify focus ring disappears

### TC-2.3: Typing enables submit
- Type "test" into the textarea
- Verify submit button becomes enabled (opacity changes from 0.4 to 1)
- Clear all text: verify submit button becomes disabled again

### TC-2.4: Enter submits
- Type a question into the textarea
- Press Enter
- Verify the loading state appears (input becomes disabled)
- Verify the question text remains in the input

### TC-2.5: Shift+Enter creates newline
- Type some text
- Press Shift+Enter
- Verify a new line is created (textarea height increases)
- Verify the form is NOT submitted

### TC-2.6: Submit button click
- Type a question
- Click the submit button (arrow icon)
- Verify loading state appears

### TC-2.7: Empty submission blocked
- Leave input empty (or whitespace only)
- Press Enter: verify nothing happens
- Click submit button: verify nothing happens

### TC-2.8: Loading state
- Submit a question
- Verify input shows a spinner (replaces arrow icon)
- Verify input is disabled (opacity 0.5)
- Verify typing is blocked during loading

### TC-2.9: Prompt input mode
- Click settings button to switch to "Input box" mode
- After pivoting a cell (see §4.4), verify the generated prompt text appears in the input
- Verify the input border pulses with accent color briefly

### TC-2.10: Auto-resize textarea
- Type enough text to exceed one line
- Verify textarea grows up to max-height (100px)
- Verify scrollbar appears after max-height

---

## 3. Welcome Screen

### TC-3.1: Welcome state renders
- On initial load (before any query), verify welcome content is visible
- Verify globe icon is visible
- Verify heading: "Welcome to Scholarly Explorer"
- Verify description: "Ask a question about the scholarly literature to begin exploring."

### TC-3.2: Example questions are clickable
- Verify "Try asking:" label is visible
- Verify three example questions are listed:
  - "Who are the most prolific authors?"
  - "Which venues have the most publications?"
  - "How has publication output changed over time?"
- Hover over each example: verify text color changes to accent (blue)
- Click an example: verify loading state begins

### TC-3.3: Example questions are keyboard accessible
- Tab to an example button
- Verify focus ring is visible (accent color)
- Press Enter: verify loading state begins

### TC-3.4: Welcome disappears after query
- Submit a question
- Verify welcome content is no longer visible
- Verify results workspace is shown instead

---

## 4. Loading State

### TC-4.1: Loading stages display sequentially
- Submit a question
- Verify these stages appear in order with a spinner:
  1. "Interpreting question..." (progress bar ~25%)
  2. "Preparing search..." (progress bar ~50%)
  3. "Querying scholarly data..." (progress bar ~75%)
  4. "Analyzing results..." (progress bar ~95%)
- Verify each stage has a spinning animation

### TC-4.2: Progress bar animation
- During loading, verify the progress bar fills progressively
- Verify the bar transitions smoothly between stages

### TC-4.3: Loading blocks interaction
- During loading, verify the search input is disabled
- Verify no other interactive elements are clickable

### TC-4.4: Loading completes
- After the final stage, verify loading state disappears
- Verify results are displayed

---

## 5. Faceted Table

### TC-5.1: Default results (authors target)
- Submit a question (e.g., "Who are the most prolific authors?")
- After loading, verify the table appears with:
  - Header row: "Authors", "Venues", "Years"
  - 10 data rows (Author A through Author J)
  - Table caption: "10 authors"

### TC-5.2: Target facet column visually distinguished
- Verify the "Authors" column header has:
  - Blue/accent left border (3px)
  - Light blue background
  - Blue text color
- Verify the "Authors" column cells have:
  - Blue/accent left border
  - Light blue background
  - Bold font weight

### TC-5.3: Non-target cells are interactive
- Hover over a numeric cell (e.g., "12" in Author A row, Venues column)
- Verify the cell background changes to a subtle hover color
- Verify the cursor changes to pointer
- Verify the cell has `role="button"` and `tabindex="0"`

### TC-5.4: Cell keyboard accessibility
- Tab to a numeric cell
- Verify focus ring is visible (accent color)
- Press Enter: verify pivot action triggers
- Tab to another cell, press Space: verify pivot action triggers

### TC-5.5: Cell aria-label
- Inspect a numeric cell (e.g., Author A row, Venues column)
- Verify `aria-label` is "Explore 12 venues"

### TC-5.6: Table data accuracy
- Verify Author A row shows: Author A | 12 | 5 | 42
- Verify Author D row shows: Author D | 15 | 7 | 58
- Verify Author J row shows: Author J | 5 | 3 | 18

### TC-5.7: Table horizontal scroll
- On a narrow viewport (e.g., 600px width), verify the table scrolls horizontally
- Verify the target column header remains sticky when scrolling

---

## 6. Pivot / Cell Click

### TC-6.1: Pivot to venues
- Submit a question to see authors table
- Click the numeric cell "12" in Author A row, Venues column
- Verify:
  - A filter pill appears: "Author = Author A" with an x button
  - Target badge changes to "Target: Venues"
  - Table now shows Venue Alpha, Venue Beta, etc.
  - Table caption shows "5 venues"
  - "Authors" column is no longer the target

### TC-6.2: Pivot to years
- From the authors table, click "5" in Author A row, Years column
- Verify:
  - Filter pill: "Author = Author A"
  - Target badge: "Target: Years"
  - Table shows 2022-2025

### TC-6.3: Pivot from venue to authors
- First pivot to venues (click Author A -> Venues)
- Then click "15" in Venue Alpha row, Authors column
- Verify:
  - Two filter pills: "Author = Author A" and "Venue = Venue Alpha"
  - Target badge: "Target: Authors"
  - Table shows filtered authors

### TC-6.4: Pivot generates prompt
- Click a numeric cell
- If prompt mode is "tooltip": verify a tooltip appears near the cell with a generated question
- If prompt mode is "input": verify the input box is populated with a generated question

### TC-6.5: Pivot updates observations
- After pivoting, verify the observations panel still shows content
- Verify follow-up questions are still present

---

## 7. Active Filters

### TC-7.1: Filter pill renders
- After a pivot, verify a filter pill appears
- Verify it shows: "[FacetLabel] = [value]"
- Verify it has an x button

### TC-7.2: Multiple filters
- Pivot twice (e.g., Author -> Venue -> Year)
- Verify two filter pills appear

### TC-7.3: Remove filter
- Click the x button on a filter pill
- Verify the filter is removed
- If it was the last filter, verify:
  - Target badge disappears
  - Table resets to empty state
  - Observations and follow-ups clear

### TC-7.4: Filter remove is keyboard accessible
- Tab to the x button on a filter pill
- Verify focus ring is visible
- Press Enter: verify filter is removed

### TC-7.5: Filter aria-label
- Inspect the x button
- Verify `aria-label` is "Remove filter: Author = Author A"

---

## 8. Sorting

### TC-8.1: Sort buttons render
- Verify sort buttons appear in the toolbar: "Author", "Venue", "Year", "Publication"
- Verify they are on the right side of the toolbar

### TC-8.2: Sort ascending
- Click "Publications" sort button
- Verify the button becomes active (blue background/border)
- Verify an up arrow appears next to "Publications"
- Verify the table rows are sorted by publication count ascending

### TC-8.3: Sort descending
- Click "Publications" again
- Verify a down arrow appears
- Verify the table rows are sorted descending

### TC-8.4: Sort reset
- Click "Publications" a third time
- Verify the sort indicator disappears
- Verify the table returns to default order

### TC-8.5: Sort different facets
- Click "Venue" sort button
- Verify "Publications" sort is cleared
- Verify "Venue" becomes active

### TC-8.6: Sort clears on pivot
- Sort by publications
- Click a numeric cell to pivot
- Verify the sort is cleared after pivot

### TC-8.7: Sort button keyboard accessible
- Tab to a sort button
- Press Enter: verify sort activates

---

## 9. Observations Panel

### TC-9.1: Panel renders after query
- Submit a question
- Verify the observations panel appears on the right side
- Verify "AI Observations" badge is visible (blue pill)

### TC-9.2: Observations display
- Verify 4 observation items are displayed
- Each observation should have:
  - A left blue border accent
  - An info icon
  - Observation text
- Verify the text is from the mock data

### TC-9.3: Observations visually distinct from data
- Verify the observations panel has a different background color than the table
- Verify the "AI Observations" badge clearly indicates AI-generated content

### TC-9.4: Empty observations state
- If observations are empty, verify message: "Observations will appear here after a query."

---

## 10. Follow-up Questions

### TC-10.1: Follow-up questions render
- After a query, verify "Suggested Questions" header is visible
- Verify 4 follow-up question buttons are displayed

### TC-10.2: Follow-up button interaction
- Hover over a follow-up button
- Verify border changes to accent color
- Verify background changes to light accent
- Verify the arrow icon moves right slightly

### TC-10.3: Follow-up click triggers query
- Click "How has publication output changed over time?"
- Verify:
  - The input is populated with this question
  - Loading state begins
  - New results appear after loading

### TC-10.4: Follow-up keyboard accessible
- Tab to a follow-up button
- Verify focus ring is visible
- Press Enter: verify query starts

---

## 11. Prompt Tooltip

### TC-11.1: Tooltip appears on cell hover (tooltip mode)
- Ensure settings is in "Tooltip" mode (default)
- Hover over a numeric cell
- Verify a tooltip appears near the cell
- Verify the tooltip contains a generated question (e.g., "Which venues has Author A published in?")

### TC-11.2: Tooltip disappears on cell leave
- Move mouse away from the cell
- Verify the tooltip disappears

### TC-11.3: Tooltip positioning
- Hover over a cell near the right edge of the viewport
- Verify the tooltip does not overflow the viewport

### TC-11.4: Tooltip in input mode
- Switch settings to "Input box" mode
- Hover over a numeric cell
- Verify NO tooltip appears
- Verify the input box gets populated instead

---

## 12. Unsupported Question

### TC-12.1: Unsupported question detection
- Type a question containing "h-index" (e.g., "What is the h-index of Author A?")
- Submit
- Verify loading stages complete
- Verify an unsupported state message appears:
  - Warning icon (yellow)
  - "This question cannot currently be answered"
  - "using the available scholarly data."
  - "You could try:" header
  - 4 suggestion buttons

### TC-12.2: Unsupported suggestion click
- Click one of the suggestion buttons (e.g., "Which authors published in Venue Alpha?")
- Verify a new query starts with that question
- Verify results appear

### TC-12.3: Unsupported keywords
- Test these keywords trigger unsupported state:
  - "citations"
  - "h-index"
  - "impact factor"
  - "co-author"
  - "download"
  - "full text"

---

## 13. Error State

### TC-13.1: Error state renders
- The ErrorState component exists for `type: 'generic'` and `type: 'unavailable'`
- Currently, the mock data only triggers `unsupported` type
- Verify the ErrorState component exists and renders correctly if triggered

### TC-13.2: Retry button
- If an error state is shown, verify "Try again" button is visible
- Click "Try again": verify a new query starts

---

## 14. Responsive Behavior

### TC-14.1: Desktop layout (>1024px)
- Verify two-column grid: table (fluid) + insights panel (360px)
- Verify max-width is 1200px, centered

### TC-14.2: Tablet layout (768-1024px)
- Resize to 900px width
- Verify insights panel narrows to 300px
- Verify layout remains two-column

### TC-14.3: Mobile layout (<768px)
- Resize to 375px width
- Verify layout switches to single column
- Verify table appears above insights panel
- Verify table scrolls horizontally if needed
- Verify toolbar wraps vertically

### TC-14.4: Welcome screen responsive
- On mobile (375px), verify welcome content is centered
- Verify examples box takes full width

---

## 15. Accessibility

### TC-15.1: Keyboard navigation
- Tab through all interactive elements on the page
- Verify focus order is logical: header settings -> search input -> submit button -> table cells -> sort buttons -> filter pills -> follow-up buttons
- Verify all focusable elements have visible focus indicators

### TC-15.2: Screen reader support
- Verify table headers use `<th scope="col">`
- Verify loading state has `role="status"` and `aria-live="polite"`
- Verify error/unsupported states have `role="alert"`
- Verify interactive cells have `role="button"`
- Verify filter remove buttons have descriptive `aria-label`
- Verify settings button has `aria-label` and `aria-pressed`

### TC-15.3: Color contrast
- Verify text is readable against backgrounds
- Verify important states are not communicated through color alone (e.g., sort indicators use arrows, not just color)

---

## 16. Edge Cases

### TC-16.1: Rapid submission
- Submit a question, then immediately try to submit another
- Verify the second submission is blocked (loading guard)

### TC-16.2: Empty table after filter removal
- Pivot to create a filter
- Remove the filter
- Verify the table shows the empty state message

### TC-16.3: Sort then pivot
- Sort by a column
- Click a cell to pivot
- Verify sort is cleared and new data is shown

### TC-16.4: Multiple pivots in sequence
- Author -> Venue (click Author A's venue count)
- Venue -> Year (click Venue Alpha's year count)
- Verify each pivot adds a filter and changes the target
- Verify removing a filter mid-chain works correctly

### TC-16.5: Browser back/forward
- After navigating through states, use browser back button
- Verify the app handles this gracefully (no crash)

---

## 17. Known Issues to Verify Fixed

### TC-17.1: No infinite loading spinner
- Submit any valid question
- Verify loading completes and does not get stuck on "Processing..."

### TC-17.2: Table renders correctly
- Verify no layout shift when table appears
- Verify columns align properly

### TC-17.3: No console errors
- Open browser DevTools console
- Perform a full interaction flow (submit -> pivot -> sort -> filter -> follow-up)
- Verify no JavaScript errors in console

---

## 18. Visual Regression Checklist

| Element | Expected |
|---------|----------|
| Header bg | White, bottom border |
| Logo | Blue square with globe icon |
| Search input | Pill shape, centered, max 900px |
| Table header | Gray bg, small semibold text |
| Target column | Blue left border, light blue bg |
| Filter pills | Blue bg, pill shape, x button |
| Sort active | Blue bg/border, arrow indicator |
| Observations | Gray bg, blue left border on items |
| Follow-up buttons | Full-width, subtle border, hover accent |
| Loading spinner | Blue top border, spinning |
| Progress bar | Blue fill, animated |

---

## Test Execution Checklist

- [ ] All TC in section 1 (Header) pass
- [ ] All TC in section 2 (Search) pass
- [ ] All TC in section 3 (Welcome) pass
- [ ] All TC in section 4 (Loading) pass
- [ ] All TC in section 5 (Table) pass
- [ ] All TC in section 6 (Pivot) pass
- [ ] All TC in section 7 (Filters) pass
- [ ] All TC in section 8 (Sorting) pass
- [ ] All TC in section 9 (Observations) pass
- [ ] All TC in section 10 (Follow-up) pass
- [ ] All TC in section 11 (Tooltip) pass
- [ ] All TC in section 12 (Unsupported) pass
- [ ] All TC in section 13 (Error) pass
- [ ] All TC in section 14 (Responsive) pass
- [ ] All TC in section 15 (Accessibility) pass
- [ ] All TC in section 16 (Edge cases) pass
- [ ] All TC in section 17 (Known issues) pass
- [ ] All TC in section 18 (Visual) pass

**Total test cases: 55**
