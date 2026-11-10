---
name: workspace
description: |
  Track project work in Taskwarrior with tickets that record the reasoning for
  each design choice. Use to create a ticket, start or finish work, replace a
  ticket when its decision changes, show the state of work in a project, show
  how a task relates to other tasks, or explain the current task. Use it also
  to set up a workspace that organizes work around tickets, to draft or
  review a proposal document, to fork the session context for one ticket,
  or to close out a ticket with a conclusion document. Use when the user
  says "task", "ticket", "todo", "backlog", "what is next", "what is
  blocked", "status of the work", "explain this task", "workspace",
  "proposal", "proposal document", "fork the context", "conclusion
  document", or "close out". All projects share one Taskwarrior database. Tickets are created only
  through the bundled tw-new script, which validates the ticket before it
  creates the task.
---

# Workspace

Taskwarrior keeps one task database for all projects, in `~/.task/`. Each task
is a ticket: a one-line title, plus one annotation that holds the reasoning.

## Rules for every command

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

## Set up a workspace

A workspace organizes its work around tickets: proposal documents and
conclusion documents.

- To set up a new workspace, run
  `~/.pi/agent/skills/workspace/scripts/tw-check --init <path>`.
- To make sure that a workspace is complete, run
  `~/.pi/agent/skills/workspace/scripts/tw-check <path>`.

Read `references/workspace.md` for the layout and the lifecycle.

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

## Show how a task relates to other tasks

- `+BLOCKED` tasks wait on other tasks. `+BLOCKING` tasks stop other tasks.
- To list each dependency in a project as an edge, run this command:
  ```bash
  task rc.verbose=nothing project:<p> export \
    | jq -r '.[] | select(.depends) | .uuid[0:8] as $u | .depends[] | "\($u) --> \(.[0:8])"'
  ```
  Each line shows that the first task waits on the second task.
- To show the relations to the user, read
  `~/.pi/agent/skills/show-me/SKILL.md` and follow it.

## Explain a task

1. Read the full ticket:
   `task rc.verbose=nothing <uuid> info`
2. Read the tasks that it waits on, and the tasks that wait on it.
3. Explain the task with the `simple-english` rules: the problem, the
   decision, and the reason for the decision.
4. If the task has relations, read `~/.pi/agent/skills/show-me/SKILL.md` and
   follow it. Show the task and its neighbors.
