# pi-ds-rivlanm — a pi harness

This repo holds the configuration, the skills, and the custom agents of
a pi coding-agent harness, plus a record of the source of each external
part. It does not install itself. The pi agent of the user installs it:
point the agent at `ADOPT.md` and approve each choice.

## Layout

The diagram shows the idea; the table gives the full list.

![Repo structure: the user's agent installs picked items](diagrams/readme/repo-structure.svg)

Diagrams in this document use the D2 theme Neutral Default.

- `harness content`: the files that pi reads. The agent installs the
  items that the user picks.
- `maintenance tools`: `check.sh`, `update.py`, and `rebuild.py`. They
  check and maintain. They install nothing.
- `the pi agent of the user`: follows `ADOPT.md`. It asks the user
  before it overwrites anything.
- `live system`: the directories that pi reads, `~/.pi/agent/` and
  `~/.agents/`.

| Path | Installed to | Contents |
|---|---|---|
| `AGENTS.md`, `settings.json`, `doc-preview-header.html` | `~/.pi/agent/` | Global instructions and pi settings |
| `skills/` | `~/.pi/agent/skills/` | Seven skills: six ours, `show-me` vendored from its upstream |
| `subagent-manager/agents/` | `~/.pi/agent/subagent-manager/agents/` | `ws-coder`, `ws-architect`, and `ws-researcher`: forks of the shipped coder, architect, and researcher for the workflow |
| `subagent-manager/upstream/` | — | Pristine shipped agents at the pinned version. Merge base for rebuilds |
| `manifest.toml` | — | Source and pinned version of each external part |
| `check.sh` | — | Reports missing tool dependencies, with install hints |
| `update.py` | — | Reports the status of each pin against upstream, with diffs |
| `rebuild.py` | — | Re-applies agent customizations after a package update |
| `diagrams/` | — | D2 sources and renders for this README |
| `tests/adoption/` | — | Docker test: the adoption flow, then one ticket's full life in a workspace |

## What the harness gives you

The harness holds two products: the standards and the workflow. You can
adopt the standards alone. The workflow needs the standards.

### The standards

Five skills. Each skill works alone.

| Skill | Purpose |
|---|---|
| `code-standards` | Functional-first design, docstrings, separation of concerns, naming; per-language guides and lint runners for Python, Go, Java, TypeScript |
| `testing-standards` | Decides whether a test earns a permanent place: it must catch a named failure |
| `simple-english` | Writes and rewrites prose with Simplified Technical English and Strunk & White rules |
| `d2-diagrams` | Authors D2 diagrams that convey one idea each. The first choice for a diagram in a document. Needs the `d2` tool |
| `show-me` | Explains a topic visually in the conversation: call trees, component trees, diffs. Used by the main session. Vendored from its upstream |

### The workflow

The workflow takes one item of work from a ticket to a recorded result.
It runs in a workspace: one directory that holds the documents and the
repositories of one body of work.

1. You define a ticket. The `tw-new.py` script validates the ticket and
   creates it in Taskwarrior.
2. If the work needs facts first, the `ws-researcher` agent writes a research
   document.
3. If the ticket needs a design, the `ws-architect` agent writes a proposal
   document.
4. You settle the design in a socratic review, one question at a time.
5. The `ws-coder` agent implements the approved proposal. You can also do the work
   in the main session.
6. A conclusion document records the result. The `tw-close.py` script
   links the document to the ticket.

| Part | Purpose | Reads these standards |
|---|---|---|
| `workspace` skill | Creates and manages a workspace: tickets, proposal documents, research documents, conclusion documents, a scratch area, and the repositories | `simple-english`, `show-me` |
| `socratic-review` skill | Works through a technical document with you, one question at a time | — |
| `ws-architect` agent | Drafts the proposal document | `d2-diagrams`, `simple-english` |
| `ws-researcher` agent | Writes the research document | `simple-english`, `d2-diagrams` |
| `ws-coder` agent | Implements the work | `code-standards`, `testing-standards` |

The workflow needs Taskwarrior, pandoc, jq, and pi-subagent-manager.

## Adopt the harness

```sh
git clone https://github.com/rivera-lanasm/pi-ds-rivlanm.git ~/pi-harness
```

Then ask your pi agent to follow `ADOPT.md`. The agent checks the tools,
shows each skill collision with a diff, installs the skills you pick,
combines the global `AGENTS.md` without losing a rule of yours, merges
`settings.json` without losing your provider or your extensions,
installs the pinned extension, and copies the custom agents. Your own
skills stay where they are. Nothing is removed and nothing is overwritten
without your approval.

Run `./check.sh` to see every tool the harness expects, with the install
command for each missing one. Missing tools disable only the skills that
need them.

Supported platforms: Linux and macOS. The container test runs Debian.
Homebrew installs every dependency; note that Homebrew ships Taskwarrior
3 while the test runs 2.6 — report differences you hit on 3.

## Private skills

A skill in `~/.pi/agent/skills/` that is not in this repo is private by
default. Nothing in the repo collects it, moves it, or removes it.

## Update an external part

```sh
uv run update.py                   # status of every external part
uv run update.py show-me           # upstream log and diffs for one part
```

`update.py` changes nothing. The diagram shows the flow: report, install
the pin, merge.

![Update flow: update.py reports, pi installs the pin, rebuild.py merges](diagrams/readme/update-flow.svg)

After you review the diff:

- **git skill** (`show-me`): merge the upstream changes into
  `skills/<name>`. Then set `base` in `manifest.toml` to the new upstream
  commit, and copy the skill into the live directory. The diffs show the
  upstream changes and our changes separately. `simple-english` was once
  tracked this way; it is now our own skill. See the note in
  `manifest.toml`.
- **npm package** (`pi-subagent-manager`):
  1. Set the new version in the pin in `settings.json` and in
     `manifest.toml`.
  2. Run `pi install npm:pi-subagent-manager@<new-pin>`. Do not use
     `pi update --extensions` for this step: it skips a pinned package
     that is not installed.
  3. Run `uv run rebuild.py`. This command three-way merges each
     customized agent in `subagent-manager/agents/` against the new
     installed version, with `subagent-manager/upstream/` as the base.
     Conflicts leave markers for manual resolution.
  4. Review with `git diff`. Copy the merged agents into
     `~/.pi/agent/subagent-manager/agents/`. Commit.

## What is not in this repo, and why

- `auth.json` — credentials.
- `sessions/`, `models-store.json`, `npm/`,
  `subagent-manager/.import-offered` — state that pi regenerates.
- `bin/rg` — a binary. Install ripgrep through your package manager.
- `settings.json` holds no secrets, so git tracks it. It carries no
  provider, model, or theme. The merge in `ADOPT.md` keeps those from
  the live file.
