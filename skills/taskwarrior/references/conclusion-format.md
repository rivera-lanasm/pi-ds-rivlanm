# Conclusion document format

A conclusion document holds the result of one ticket. It has two jobs:

- During the work, it records progress. A new session can continue the work
  from the document.
- At close-out, it holds the summary. The ticket points to it.

One file for each ticket: `conclusions/<task-id>.md`. For `<task-id>`, use
the task ID from the plan document. If the plan document has no task IDs,
use the first 8 characters of the ticket UUID.

## Format

```markdown
# <task-id>: <title>

Ticket: <uuid>
Status: in progress

## Goal

One or two sentences. What the ticket must achieve.

## Progress

- YYYY-MM-DD: One line. What changed at this boundary.

## Done

- One line for each completed item.

## Decisions

- **Decision**: The reason for the decision.

## Artifacts

- The files, commits, and documents that the work produced.

## Open items

- What remains. Write "None" when the ticket is complete.
```

## Rules

- Write the document with the simple-english rules.
- Write one fact per line. Each line stands alone.
- During the work, add one dated line to Progress at each natural boundary.
- At close-out, fill Done, Decisions, Artifacts, and Open items. Set Status
  to `done`.
- Keep the document under one page. The document points to the artifacts. It
  does not copy their content.
