# Context forking for one ticket

A context fork keeps the main session free of the context that one ticket
adds. The work happens on a branch of the session tree. At close-out, the
user returns to the fork point. The main session continues without the
branch.

## How it works

Pi stores a session as a tree of entries. The model receives only the active
branch. The user navigates the tree with `/tree` and continues from an
earlier entry. Navigation changes the context. It does not change the disk.

A fork for one ticket uses this mechanism:

1. The work of the ticket starts at a new user message. This message marks
   the fork point.
2. The agent does the work. The branch holds each tool result and each file
   that the work reads.
3. At close-out, the user navigates back to the fork point. The branch stays
   in the session file. The active context no longer includes it.

## When to fork

A fork is a choice for each ticket. It is never the default. Both conditions
must be true:

- The work needs the main session and the user, for example a review or a
  design discussion.
- The work can add heavy context: large files, long command output, or many
  tool turns.

If the work is a self-contained part, delegate it to the coder subagent.
If the work is small, use plain work.

## Procedure

The agent advises. The user does the two navigation steps by hand.

1. If the ticket needs a fork, say so in one sentence. Give the reason.
2. Tell the user:

   > Start ticket <ticket-id> in a new message. That message is the fork point.

3. Wait for the user to start the ticket. This is a user action.
4. Do the work. At each natural boundary, add one dated line to the Progress
   section of the conclusion document.
5. When the work is done, close out the ticket. Follow the "Close out a
   ticket" section of `SKILL.md`.
6. Tell the user:

   > Ticket <ticket-id> is closed out. The conclusion document is at
   > `conclusions/<ticket-id>.md`. Open `/tree`. Go to the entry before the
   > first message of this ticket. Continue from there. When Pi offers a
   > summary of the branch, decline it. The conclusion document holds the
   > summary.

7. Wait for the user to navigate. This is a user action.
8. Continue the main session from the fork point. One line records the
   ticket: its ID and the path to the conclusion document.

## Rules

- Never start the work of a forked ticket in the middle of an unrelated
  turn. The fork point must be a clean user-message boundary.
- Do not propose a fork for a small task.
- The branch stays in the session file. The user can return to it with
  `/tree` at any time.
