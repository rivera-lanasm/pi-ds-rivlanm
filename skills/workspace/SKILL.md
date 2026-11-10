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

## Rules for every ticket command

- Add `rc.confirmation=off` to each `task` command that changes data. Without
  it, Taskwarrior can stop and wait for an answer that you cannot give.
- Add `rc.verbose=nothing` to each `task` command that reads data.
- Refer to a task by its UUID, or by the first 8 characters of the UUID.
- Do not use the short numeric IDs across steps. Taskwarrior renumbers them
  when a task is done.
- Do not create a task with `task add` or `task annotate`. Use `tw-new`.

## Find the project name

The workspace AGENTS.md declares the project name in a `Project:` line.
Read it there first.

When the workspace has no AGENTS.md, or the file gives no project name, use
the name of the directory:

```bash
basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
```

A subproject adds a dot and a name, for example `notes.auth`. In the
commands below, `<p>` is the project name.

## Ask before you create

Do not run `tw-new` until the user agrees to the ticket. A ticket with weak
reasoning is worse than no ticket.

1. Ask the user whether they want a ticket. Say in one sentence what the
   ticket covers. If the user asked for the ticket, skip this step.
2. Write the ticket from the conversation. The template in
   `assets/ticket-template.json` names the fields. Ask the user about each
   field that the conversation does not answer. Do not invent an answer.
3. When the reasoning does not exist yet, the task needs design work
   first. Create a design ticket: the architect drafts a proposal
   document, and the socratic review settles the design. Create the
   implementation ticket after the user approves the proposal. It depends
   on the design ticket, and its fields come from the proposal document.
4. Show the user the ticket JSON. If the user confirms it, continue with
   the steps in "Create a ticket".

## Create a ticket

1. Load the `simple-english` skill. Write every bullet with its rules.
2. Read the ticket schema:
   ```bash
   ~/.pi/agent/skills/workspace/scripts/tw-new --schema
   ```
3. Write the ticket as JSON. Start from the template in
   `assets/ticket-template.json` and replace each value. Never send the
   template to `tw-new` unchanged. Each bullet is one line of 3 to 200
   characters.
4. Send the JSON to `tw-new` on stdin:
   ```bash
   ~/.pi/agent/skills/workspace/scripts/tw-new <<'EOF'
   {
     "title": "Add text search to notes",
     "project": "notes.search",
     "tags": ["feature"],
     "depends": [],
     "problem": ["Notes cannot be found by their text"],
     "decision": ["Search the note files with ripgrep"],
     "artifacts": ["A search module in the notes package"],
     "risks": [
       {"risk": "Search is slow on a large repository",
        "detection": "One search takes more than 2 seconds"}
     ],
     "done_when": ["A search shows each match with its line number"]
   }
   EOF
   ```
5. If `tw-new` exits with 0, it prints the UUID of the new task. Keep this
   UUID.
6. If `tw-new` exits with 1, it prints one line for each error. Each line
   gives the field and the rule. Correct the JSON and send it again.
   `tw-new` creates no task when it finds an error.

`depends` holds the UUIDs of tasks that must be done first. `tw-new` stops if a
UUID does not match a task.

## Start and finish work

- To start a task: `task rc.confirmation=off <uuid> start`
- To finish a task: `task rc.confirmation=off <uuid> done`

## Replace a ticket when its decision changes

Do not edit the reasoning of a ticket. Replace the ticket:

1. Create the new ticket with `tw-new`. Write the new decision and its reasons.
2. Close the old ticket as canceled:
   `task rc.confirmation=off <old-uuid> delete`

Use `delete`, not `done`. The old ticket was not finished.

## Fork the session context for one ticket

A fork is a choice for each ticket. It is never the default. When the work
needs the main session and the user, and the work can add heavy context
(large files, long command output, or many tool turns), read
`references/context-forking.md` and follow it.

The user does two steps by hand: the user marks the fork point, and the user
navigates back to the fork point at close-out. The agent cannot do these
steps.

## Close out a ticket

1. Finish the conclusion document. Read `references/conclusion-format.md`
   and follow it.
2. Run `~/.pi/agent/skills/workspace/scripts/tw-close <uuid> [document]`.
   When the document name is not `conclusions/<uuid-prefix>.md`, pass the
   path as the second argument. The script makes sure that the ticket is
   open and that the document is complete. Then it annotates the ticket with
   the path and prints the next steps for the user.
3. When the work used a context fork, tell the user to navigate back to
   the fork point. This is a user action. `references/context-forking.md`
   gives the exact prompt.

## Show the state of work

Each command prints one line for each task: the UUID prefix, the status, and
the title.

```bash
Q='.[] | "\(.uuid[0:8])  \(.status)  \(.description | split("\n")[0])"'
task rc.verbose=nothing project:<p> +ACTIVE export | jq -r "$Q"     # started
task rc.verbose=nothing project:<p> +READY export | jq -r "$Q"      # can start now
task rc.verbose=nothing project:<p> +BLOCKED export | jq -r "$Q"    # waits on other tasks
task rc.verbose=nothing project:<p> status:completed end.after:today-7d export | jq -r "$Q"
task rc.verbose=nothing project:<p> status:pending count
```

To give a summary, use these groups in this order: started, ready, blocked,
done in the last 7 days. Write the summary with the `simple-english` rules.

## Show how a ticket relates to other tickets

- `+BLOCKED` tasks wait on other tasks. `+BLOCKING` tasks stop other tasks.
- To list each dependency in a project as an edge, run this command:
  ```bash
  task rc.verbose=nothing project:<p> export \
    | jq -r '.[] | select(.depends) | .uuid[0:8] as $u | .depends[] | "\($u) --> \(.[0:8])"'
  ```
  Each line shows that the first task waits on the second task.
- To show the relations to the user, read
  `~/.pi/agent/skills/show-me/SKILL.md` and follow it.

## Explain a ticket

1. Read the full ticket:
   `task rc.verbose=nothing <uuid> info`
2. Read the tasks that it waits on, and the tasks that wait on it.
3. Explain the task with the `simple-english` rules: the problem, the
   decision, and the reason for the decision.
4. If the task has relations, read `~/.pi/agent/skills/show-me/SKILL.md` and
   follow it. Show the task and its neighbors.
