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
| `subagent-manager/agents/` | `~/.pi/agent/subagent-manager/agents/` | Customized coder, architect, and researcher for pi-subagent-manager |
| `subagent-manager/upstream/` | — | Pristine shipped agents at the pinned version. Merge base for rebuilds |
| `manifest.toml` | — | Source and pinned version of each external part |
| `check.sh` | — | Reports missing tool dependencies, with install hints |
| `update.py` | — | Reports the status of each pin against upstream, with diffs |
| `rebuild.py` | — | Re-applies agent customizations after a package update |
| `diagrams/` | — | D2 sources and renders for this README |
| `tests/adoption/` | — | Docker test: the adoption flow, then one ticket's full life in a workspace |

## The skills

| Skill | Purpose |
|---|---|
| `workspace` | Creates and manages a workspace: tickets, proposal documents, research documents, conclusion documents, a scratch area, and the repositories of one body of work |
| `code-standards` | Functional-first design, docstrings, separation of concerns, naming; per-language guides and lint runners for Python, Go, Java, TypeScript |
| `simple-english` | Writes and rewrites prose with Simplified Technical English and Strunk & White rules |
| `socratic-review` | Works through a technical document with you, one question at a time |
| `testing-standards` | Decides whether a test earns a permanent place: it must catch a named failure |
| `d2-diagrams` | Authors D2 diagrams that convey one idea each |
| `show-me` | Explains a topic visually: call trees, component trees, diffs. Vendored from its upstream |

The pieces depend on each other, so picking à la carte needs the map:

- The **architect** uses the `workspace` skill (the proposal format and
  the ticket lifecycle), the `d2-diagrams` skill, and the
  `simple-english` skill.
- The **researcher** uses `simple-english`, `d2-diagrams`, and the
  show-me formats.
- The **coder** uses `code-standards` and `testing-standards`.
- The **workspace** skill needs Taskwarrior, pi-subagent-manager, and
  pandoc for the render script.

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
