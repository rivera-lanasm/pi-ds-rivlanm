# Workspace layout

A workspace is a dedicated directory that organizes work around
Taskwarrior tickets. It is not a repository. It holds the tracking
documents and one or more repositories. This document gives the standard
layout, the lifecycle of one ticket, and the rules for the workspace files.

A workspace can start small. Tickets and one directory are enough. Add each
part when the work earns it.

## Layout

| Item | Purpose |
|---|---|
| `AGENTS.md` | The session rules for the workspace. Read "The workspace AGENTS.md". |
| `workspace.toml` | The declared parts that the check reads. |
| `research/` | One research document for each research question. |
| `proposals/` | One proposal document for each ticket that needs a design before implementation. |
| `conclusions/` | One conclusion document for each ticket. |
| `scratch/` | One-off scripts and ephemeral tests. |
| `repos/` | The repositories of the workspace. Each repository has one role. |

The documents (`research/`, `proposals/`, `conclusions/`), `AGENTS.md`, and
`workspace.toml` are tracked: they are the durable record of the workspace,
and documents and tickets can point at them. `scratch/` is ephemeral:
anything in it can be deleted at any time, and nothing points at it. When a
scratch script earns permanence, it moves into a work repo. Git tracks the
code inside each repository. The documents track the reasoning.

The ticket ID is the first 8 characters of the ticket UUID. It names
each per-ticket document: `proposals/<ticket-id>.md` and
`conclusions/<ticket-id>.md`.

## The repositories

Each repository in `repos/` has one role:

- A work repo is a repository that the work changes. Tickets land commits
  here.
- A context repo is a repository that the work reads only: helpers,
  examples, upstream sources.

Declare each repository in `workspace.toml`:

```toml
[repos]
work = ["notes-app"]
context = ["notes-legacy"]
```

The check resolves each declared name at `repos/<name>` and makes sure that
it is a git repository. A directory in `repos/` that no role declares earns
a note, so the declaration stays honest.

## The workspace AGENTS.md

The file sits at the workspace root. It governs every session that opens in
the workspace, including a session that opens inside a repository.

The file holds only what the skill cannot know:

- The identity of the project: the repositories and the project name for
  tickets.
- The permission gates, for example "the agent never merges a pull
  request".
- The hard rules, for example "no new dependency without the user's
  approval".

The procedure stays in the skill. The file names the skill. It never copies
the procedure of the skill. A copy drifts, and the two texts disagree.

Keep the file short: every session loads it. Write rules and pointers, not
workflow text.

## Set up the workspace

Run once for each new workspace:

```bash
~/.pi/agent/skills/workspace/scripts/tw-check --init <path>
```

The script creates `proposals/`, `conclusions/`, an `AGENTS.md` stub with
the `Project:` line, and a `workspace.toml` stub. Fill in the stubs. Then
check the workspace:

```bash
~/.pi/agent/skills/workspace/scripts/tw-check <path>
```

The `workspace.toml` file declares the parts that the check reads:

```toml
project = "notes"

[repos]
# work = ["repo-one"]
# context = ["repo-two"]
```

Without the file, the check runs only the generic checks.

## Lifecycle of one ticket

1. Create the ticket. Follow the "Ask before you create" section of
   `SKILL.md`. When the task is too large to reason out in conversation,
   that section gives the design-ticket path.
2. The user makes two decisions: does the task need a proposal document,
   and which execution mode the work uses. Read "Pick the execution mode".
3. When the task needs a proposal document, the architect drafts it. Read
   `references/proposal-format.md` and follow it. The review ends when the
   user approves the document.
4. Do the work. The user reviews the result.
5. Close out the ticket. Follow the "Close out a ticket" section of
   `SKILL.md`. When the work used a context fork, the user navigates back
   to the fork point.

## Pick the execution mode

Pick one mode for each ticket:

- **Plain work.** The default. The agent does the work in the main session.
- **Subagent.** For a self-contained part of the work. Name the coder
  subagent. The coder works in its own context. The main session receives
  the conclusion.
- **Context fork.** When the work needs the main session and the user, and
  the work can add heavy context, the user forks the session. Heavy context
  means large files, long command output, or many tool turns. Read
  `references/context-forking.md` and follow it.

A context fork covers everything the ticket does in the main session: the
review of the proposal document and the implementation.
