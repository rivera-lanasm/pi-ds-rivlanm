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

The file sits at the workspace root. Pi loads it for every session in
the workspace, together with the global file. When the session works
inside a repository that carries its own AGENTS.md, that file loads
too, closest to the work.

The file holds only what the agent cannot work out by reading the code:

- The project name for tickets. The repositories live in
  `workspace.toml`; do not repeat them here.
- The commands, one per line, in the form you paste into a terminal: how
  to build, how to test, how to run one test, how to lint. Name only the
  commands that differ from the tool defaults.
- The permission gates, for example "the agent never merges a pull
  request".
- The hard rules, written so you can check them. "Never edit files under
  dist/, they come from the build" stops one mistake and names the cause.
  "Format the code properly" verifies nothing.
- The ticket policy: what becomes a ticket in this workspace. The skill
  sets the working limit and the creation rule; the workspace file defines
  what counts as a ticket here.
- The secrets pointer, for example "credentials live in .env, which is
  not tracked; ask before reading it". Never a secret itself.

The procedure stays in the skill. The file names the skill. It never
copies the procedure of the skill. A copy drifts, and the two texts
disagree.

When a rule belongs to one repository only, put it in that repository's
own AGENTS.md. Pi loads it beside the code it governs.

Keep the file short: every session loads it, and instruction-following
degrades as the instruction count grows. Add a line when you have typed
the same correction into a session twice. Start from the template in
`references/agents-md-template.md`.

Sources: humanlayer.dev/blog/writing-a-good-claude-md and
ssdnodes.com/learn/agents-md-and-human-md.

## Set up the workspace

Run once for each new workspace:

```bash
~/.pi/agent/skills/workspace/scripts/tw-check.py --init <path>
```

The script creates `proposals/`, `conclusions/`, an `AGENTS.md` stub with
the `Project:` line, and a `workspace.toml` stub. Fill in the stubs. Then
check the workspace:

```bash
~/.pi/agent/skills/workspace/scripts/tw-check.py <path>
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

1. Create the ticket. Follow "The user owns creation" in the "Tickets" section
   of `SKILL.md`. When the task is too large to reason out in
   conversation, that section gives the design-ticket path.
2. The user makes two decisions: does the task need a proposal document,
   and which execution mode the work uses. Read "Pick the execution mode".
3. When the task needs a proposal document, the `ws-architect` agent drafts it. Run the socratic review against the user's questions about each section. Follow the socratic-review skill. The review ends when the user approves the document.
4. Do the work. The user reviews the result.
5. Close out the ticket. Follow the "Close out a ticket" section of
   `references/tickets.md`. When the work used a context fork, the user navigates back
   to the fork point.

## Pick the execution mode

Pick one mode for each ticket:

- **Plain work.** The default. The agent does the work in the main session.
- **Subagent.** For a self-contained part of the work. Name the `ws-coder`
  subagent. The `ws-coder` agent works in its own context. The main session receives
  the conclusion. Write the brief with `brief-new.py`: read "Start a subagent" in `SKILL.md`.
- **Context fork.** When the work needs the main session and the user, and
  the work can add heavy context, the user forks the session. Heavy context
  means large files, long command output, or many tool turns. Read
  `references/context-forking.md` and follow it.

A context fork covers everything the ticket does in the main session: the
review of the proposal document and the implementation.
