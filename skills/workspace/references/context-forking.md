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

After the navigation, the agent does not know what the branch did. The last
entry in its context is its own advice to start the ticket. The user tells
the agent the result with one line, the return line.

## When to fork

A fork is a choice for each ticket. It is never the default. Both conditions
must be true:

- The work needs the main session and the user, for example a review or a
  design discussion.
- The work can add heavy context: large files, long command output, or many
  tool turns.

If the work is a self-contained part, delegate it to the `ws-coder` subagent.
If the work is small, use plain work.

## Procedure

The agent advises. The user does the two navigation steps by hand.

### On the branch

1. If the ticket needs a fork, say so in one sentence. Give the reason.
2. Tell the user:

   > Start ticket <ticket-id> in a new message. That message is the fork point.

3. Wait for the user to start the ticket. This is a user action.
4. Do the work. At each natural boundary, add one dated line to the Progress
   section of the conclusion document.
5. When the work is done, close out the ticket. Follow the "Close out a
   ticket" section of `references/tickets.md`.
6. Tell the user:

   > Ticket <ticket-id> is closed out. The conclusion document is at
   > `conclusions/<ticket-id>.md`. Open `/tree`. Go to the entry before the
   > first message of this ticket. Continue from there. When Pi offers a
   > summary of the branch, decline it. The conclusion document holds the
   > summary. Then send this line as your next message:
   >
   > `Ticket <ticket-id> is closed out. Conclusion document: conclusions/<ticket-id>.md`

7. Stop. The work on the branch is complete. The navigation is a user
   action.

### After the return

The agent is now at the fork point. Its context does not include the
branch.

1. When the user sends the return line, record the ticket as closed out.
   Do not start the work of the ticket again.
2. Do not read the conclusion document at this time. If later work needs
   a fact from the ticket, read the document then.
3. If the next message of the user is not the return line and does not
   start the ticket, ask the user one question: is the ticket closed out?
4. Continue the main session.

## Rules

- Never start the work of a forked ticket in the middle of an unrelated
  turn. The fork point must be a clean user-message boundary.
- Do not propose a fork for a small task.
- The branch stays in the session file. The user can return to it with
  `/tree` at any time.
