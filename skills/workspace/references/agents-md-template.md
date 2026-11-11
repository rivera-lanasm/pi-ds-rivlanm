# Workspace AGENTS.md template

Copy this template to the workspace root as `AGENTS.md`. Fill each
section. The workspace skill holds the procedure — tickets, documents,
layout — and this file holds what only the maintainer of this workspace
knows. Keep the file short: every session in the workspace loads it. Add
a line when you have typed the same correction into a session twice.

```markdown
# <workspace name> workspace

Project: <project name for tickets, for example notes>

This file holds the session rules for this workspace. The workspace
skill holds the procedure.

## Commands

- <work repo> — build:
- <work repo> — test one file:
- <work repo> — lint:

One command per line, in the form you paste into a terminal. Name only
the commands that differ from the tool defaults. When a command belongs
to one repository only, put it in that repository's own AGENTS.md.

## Tickets

<What becomes a ticket in this workspace. The maintainer defines it.
For example: a ticket needs a user-visible artifact; a question is
research, not a ticket.>

## Hard rules

- <Repository gate, for example: the agent never pushes to the main
  branch of a work repo.>
- <Dependency gate, for example: no new dependency without the approval
  of the maintainer.>
- <Checkable rule, for example: never edit files under dist/, they come
  from the build. "Format the code properly" is not a rule; nothing in
  it can be verified.>

## Secrets

<Where credentials live, for example: credentials live in .env, which
is not tracked. Ask before reading it. Never write a secret itself.>
```

The roles of the repositories — work and context — are declared in
`workspace.toml`. Do not restate them here.

When a rule belongs to one repository only, put it in that repository's
own `AGENTS.md`. Pi loads the nearest file for the work at hand, so the
rule loads only when that code is in scope.
