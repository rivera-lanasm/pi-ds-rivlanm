---
name: workspace
description: |
  Create and manage a workspace: one directory that holds the documents,
  the scratch area, and the repositories of one body of work. Use to set
  up or check a workspace, to add a repository as a work repo or a
  context repo, to commission a research document, to draft or review a
  proposal document, or to work the tickets that track the work: create,
  start, finish, replace, explain, show the state, show the relations,
  fork the context, close out. Tickets live in Taskwarrior. The agents
  come from pi-subagent-manager. Use when the user says "workspace",
  "research", "scratch", "repo", "task", "ticket", "todo", "backlog",
  "what is next", "what is blocked", "status of the work", "explain
  this task", "proposal", "fork the context", "conclusion document",
  or "close out". Tickets are created only through the bundled tw-new
  script, which validates the ticket before it creates the task.
---

# Workspace

The workspace skill creates and manages a workspace: one directory that
holds the documents, the scratch area, and the repositories of one body of
work. Taskwarrior holds the tickets of the workspace in one database, in
`~/.task/`. pi-subagent-manager provides the agents that work in it. The
skill guides both tools. Each Taskwarrior task is a ticket: a one-line
title, plus one annotation that holds the reasoning.

## The layout

| Part | Purpose | Tracking |
|---|---|---|
| `AGENTS.md` | The session rules for the workspace | tracked |
| `workspace.toml` | The declared parts that `tw-check` reads | tracked |
| `research/` | One research document for each research question | tracked |
| `proposals/` | One proposal document for each ticket that needs a design | tracked |
| `conclusions/` | One conclusion document for each ticket | tracked |
| `scratch/` | One-off scripts and ephemeral tests | ephemeral |
| `repos/` | The repositories of the workspace | each repo has its own git |

Tracked means: part of the durable record of the workspace. Documents and
tickets can point at a tracked item. Ephemeral means: deletable at any
time, and nothing points at it. Read `references/workspace.md` for the
full rules.

## Set up a workspace

- To set up a new workspace, run
  `~/.pi/agent/skills/workspace/scripts/tw-check --init <path>`. The script
  creates the skeleton and never overwrites an existing file.
- Fill in the stubs: the workspace `AGENTS.md` and `workspace.toml`.
- To make sure that a workspace is complete, run
  `~/.pi/agent/skills/workspace/scripts/tw-check <path>`.

Read `references/workspace.md` for the layout and the lifecycle.

## Add a repository

Clone the repository into `repos/`. Then declare its role in
`workspace.toml`:

```toml
[repos]
work = ["repo-one"]
context = ["repo-two"]
```

A work repo is a repository that the work changes. A context repo is a
repository that the work reads only: helpers, examples, upstream sources.
Run `tw-check` after each change.

## Use the scratch directory

`scratch/` holds one-off scripts and ephemeral tests. Nothing in it is
tracked: no ticket, no document, and no script points at a scratch file.
When a scratch script earns permanence, move it into a work repo.

## The tools

| Tool | What it does here | Its parts |
|---|---|---|
| Taskwarrior | Holds the tickets of every workspace in one database (`~/.task/`). | The `task` CLI; the boundary scripts `tw-new` and `tw-close`; the jq queries. |
| The tw scripts | `tw-new` validates and creates tickets. `tw-close` closes out a ticket. `tw-check` sets up and checks the workspace. | Bundled with the skill under `scripts/`. |
| pi-subagent-manager | Provides the subagents that work in the workspace. | The architect drafts proposal documents. The coder implements self-contained work. The researcher writes research documents. |

## Tickets

A ticket holds the reasoning for one item of work. The commands live in
`references/tickets.md`. Read it before you run the first ticket command
in a session.

**Ask before you create.** Do not create a ticket until the user agrees to
it. A ticket with weak reasoning is worse than no ticket.

1. Ask the user whether they want a ticket. Say in one sentence what the
   ticket covers. If the user asked for the ticket, skip this step.
2. Write the ticket from the conversation. Ask the user about each field
   that the conversation does not answer. Do not invent an answer.
3. When the reasoning does not exist yet, the design comes first: the
   architect drafts a proposal document, the socratic review settles the
   design, and the implementation ticket follows after the user approves
   it. It depends on the design ticket, and its fields come from the
   proposal document.
4. Show the user the ticket before you create the task. When the user
   confirms it, follow "Create a ticket" in `references/tickets.md`.

**Replace, never edit.** When the decision of a ticket changes, do not
edit its reasoning. Create the new ticket, then close the old ticket as
canceled. The old ticket was not finished.

**Pick one execution mode per ticket.** Plain work, a subagent, or a
context fork. Read "Pick the execution mode" in
`references/workspace.md`. A fork is never the default. The user marks
the fork point and navigates back; the agent cannot do these steps.

**Close out every ticket.** Finish the conclusion document: read
`references/conclusion-format.md`. Run `tw-close` to link the document
to the ticket. When the work used a context fork, tell the user to
navigate back to the fork point.

**Report the state with fixed groups.** Started, ready, blocked, done in
the last 7 days. Write the summary with the `simple-english` rules.

**Explain a ticket from its reasoning.** Read the ticket, the tickets it
waits on, and the tickets that wait on it. Explain the problem, the
decision, and the reason for the decision. When the ticket has relations,
read the `show-me` skill and show the ticket and its neighbors.
