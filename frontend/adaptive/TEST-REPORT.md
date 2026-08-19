# UI Testing Report: Scholarly Explorer

**Application:** Adaptive Conversational Knowledge Graph Explorer
**URL:** `http://localhost:5173`
**Test Date:** [DATE]
**Tester:** [NAME]
**Browser:** [BROWSER + VERSION]
**Resolution:** [DESKTOP/MOBILE]

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Total Test Cases | 65 |
| Passed | |
| Failed | |
| Blocked | |
| Not Executed | |
| **Pass Rate** | **%** |

### Severity Distribution

| Severity | Count |
|----------|-------|
| Critical | |
| High | |
| Medium | |
| Low | |

---

## Test Execution Results

### SUITE 1: Initial State & Welcome Screen

| Test ID | Test Case | Status | Notes |
|---------|-----------|--------|-------|
| TC-001 | Welcome screen displays on first visit | | |
| TC-002 | Header elements | | |
| TC-003 | Input field is enabled | | |

**Suite Status:** PASS / FAIL

---

### SUITE 2: Conversation Input

| Test ID | Test Case | Status | Notes |
|---------|-----------|--------|-------|
| TC-010 | Send message with Enter key | | |
| TC-011 | Send message with button click | | |
| TC-012 | Shift+Enter for new line | | |
| TC-013 | Cannot send empty message | | |
| TC-014 | Cannot send whitespace only | | |
| TC-015 | Input auto-resizes | | |

**Suite Status:** PASS / FAIL

---

### SUITE 3: Mock Response Scenarios

| Test ID | Test Case | Input | Status | Notes |
|---------|-----------|-------|--------|-------|
| TC-020 | Prolific authors query | "Who are the most prolific authors?" | | |
| TC-021 | Filter by years | "Only consider the last five years" | | |
| TC-022 | Venue pivot query | "Which venues do they publish in?" | | |
| TC-023 | Timeline query | "Show me how this changed over time" | | |
| TC-024 | Comparison query | "Compare SIGIR and CHIIR" | | |
| TC-025 | Why question | "Why is SIGIR prominent?" | | |
| TC-026 | Unsupported question | "What is the weather today?" | | |
| TC-027 | Case insensitivity | "WHO ARE THE MOST PROLICT AUTHORS" | | |

**Suite Status:** PASS / FAIL

---

### SUITE 4: Table Interactions

| Test ID | Test Case | Status | Notes |
|---------|-----------|--------|-------|
| TC-030 | Column sorting - click | | |
| TC-031 | Sort by different columns | | |
| TC-032 | Table header hover state | | |
| TC-033 | Table row hover state | | |
| TC-034 | Keyboard navigation - Tab | | |
| TC-035 | Keyboard navigation - Arrow keys | | |

**Suite Status:** PASS / FAIL

---

### SUITE 5: Filter & Pill Interactions

| Test ID | Test Case | Status | Notes |
|---------|-----------|--------|-------|
| TC-040 | Filter pill appears | | |
| TC-041 | Remove filter with × | | |
| TC-042 | Multiple filters | | |
| TC-043 | Filter persists in conversation | | |

**Suite Status:** PASS / FAIL

---

### SUITE 6: AI Observations & Suggestions

| Test ID | Test Case | Status | Notes |
|---------|-----------|--------|-------|
| TC-050 | Observation card displays | | |
| TC-051 | Observation has left border | | |
| TC-052 | Suggestion chips display | | |
| TC-053 | Click suggestion chip | | |
| TC-054 | Suggestion chip hover | | |

**Suite Status:** PASS / FAIL

---

### SUITE 7: Conversation History

| Test ID | Test Case | Status | Notes |
|---------|-----------|--------|-------|
| TC-060 | User message styling | | |
| TC-061 | Assistant message styling | | |
| TC-062 | Auto-scroll on new message | | |
| TC-063 | Conversation maintains context | | |
| TC-064 | Loading state | | |

**Suite Status:** PASS / FAIL

---

### SUITE 8: Session Persistence

| Test ID | Test Case | Status | Notes |
|---------|-----------|--------|-------|
| TC-070 | State persists on page refresh | | |
| TC-071 | Clear exploration | | |
| TC-072 | New Exploration button visibility | | |

**Suite Status:** PASS / FAIL

---

### SUITE 9: URL State

| Test ID | Test Case | Status | Notes |
|---------|-----------|--------|-------|
| TC-080 | URL with query parameter | | |

**Suite Status:** PASS / FAIL

---

### SUITE 10: Responsive Design

| Test ID | Test Case | Status | Notes |
|---------|-----------|--------|-------|
| TC-090 | Desktop layout (1920x1080) | | |
| TC-091 | Tablet layout (768px) | | |
| TC-092 | Mobile layout (375px) | | |
| TC-093 | Viewport height changes | | |

**Suite Status:** PASS / FAIL

---

### SUITE 11: Accessibility

| Test ID | Test Case | Status | Notes |
|---------|-----------|--------|-------|
| TC-100 | Keyboard-only navigation | | |
| TC-101 | Screen reader labels | | |
| TC-102 | Focus visibility | | |
| TC-103 | Color contrast | | |

**Suite Status:** PASS / FAIL

---

### SUITE 12: Visual Design Compliance

| Test ID | Test Case | Status | Notes |
|---------|-----------|--------|-------|
| TC-110 | Typography hierarchy | | |
| TC-111 | Color consistency | | |
| TC-112 | Spacing consistency | | |
| TC-113 | Border radius | | |

**Suite Status:** PASS / FAIL

---

## Bugs Found

### BUG-001
- **Test Case:** TC-XXX
- **Severity:** Critical / High / Medium / Low
- **Summary:** [One-line description]
- **Steps to Reproduce:**
  1. ...
  2. ...
- **Expected:** [What should happen]
- **Actual:** [What actually happened]
- **Screenshots:** [Attach]
- **Status:** Open / In Progress / Fixed / Won't Fix

---

### BUG-002
- **Test Case:** TC-XXX
- **Severity:** Critical / High / Medium / Low
- **Summary:** [One-line description]
- **Steps to Reproduce:**
  1. ...
  2. ...
- **Expected:** [What should happen]
- **Actual:** [What actually happened]
- **Screenshots:** [Attach]
- **Status:** Open / In Progress / Fixed / Won't Fix

---

### BUG-003
- **Test Case:** TC-XXX
- **Severity:** Critical / High / Medium / Low
- **Summary:** [One-line description]
- **Steps to Reproduce:**
  1. ...
  2. ...
- **Expected:** [What should happen]
- **Actual:** [What actually happened]
- **Screenshots:** [Attach]
- **Status:** Open / In Progress / Fixed / Won't Fix

---

*(Add more bug sections as needed)*

---

## Browser Compatibility Matrix

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Welcome screen | | | | |
| Send message | | | | |
| Table sorting | | | | |
| Keyboard navigation | | | | |
| Session persistence | | | | |
| Responsive layout | | | | |

---

## Test Evidence

### Screenshots

| Test Case | Screenshot |
|-----------|------------|
| TC-001 | [Attach] |
| TC-020 | [Attach] |
| TC-030 | [Attach] |
| TC-070 | [Attach] |

### Videos

| Test Case | Video |
|-----------|-------|
| TC-035 (Keyboard nav) | [Attach] |
| TC-100 (A11y) | [Attach] |

---

## Recommendations

### Critical Issues (Must Fix Before Release)
1. [List any critical bugs]

### High Priority Issues (Should Fix Before Release)
1. [List any high-severity bugs]

### Medium Priority Issues (Can Fix in Next Sprint)
1. [List any medium-severity bugs]

### Low Priority Issues (Backlog)
1. [List any low-severity bugs]

---

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Tester | | | |
| QA Lead | | | |
| Product Owner | | | |

---

## Appendix A: Known Limitations (Not Bugs)

These are expected behaviors based on the mock implementation:

1. Only 7 query types are recognized - Other questions get "unsupported" response
2. Filters are mock-driven - Clicking filter × removes visual pill but doesn't re-query
3. No real backend - All data is from mock responses
4. URL state only reads `q` parameter - facet/filters in URL are decoded but not applied
5. Session storage is browser-tab specific - Different tabs have separate sessions

---

## Appendix B: Test Environment Details

| Component | Version/Details |
|-----------|-----------------|
| OS | |
| Browser | |
| Screen Resolution | |
| Node.js | |
| Application Version | |
