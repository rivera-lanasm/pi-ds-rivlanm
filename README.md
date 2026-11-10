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
| `subagent-manager/agents/` | `~/.pi/agent/subagent-manager/agents/` | Customized coder and architect for pi-subagent-manager |
| `subagent-manager/upstream/` | — | Pristine shipped agents at the pinned version. Merge base for rebuilds |
| `manifest.toml` | — | Source and pinned version of each external part |
| `check.sh` | — | Reports missing tool dependencies, with install hints |
| `update.py` | — | Reports the status of each pin against upstream, with diffs |
| `rebuild.py` | — | Re-applies agent customizations after a package update |
| `tests/adoption/` | — | Docker test of the adoption flow |

## Adopt the harness

```sh
git clone https://github.com/rivera-lanasm/pi-ds-rivlanm.git ~/pi-harness
```

Then ask your pi agent to follow `ADOPT.md`. The agent checks the tools,
shows each skill collision with a diff, installs the skills you pick,
merges `settings.json` without losing your provider or your extensions,
installs the pinned extension, and copies the custom agents. Your own
skills stay where they are. Nothing is removed and nothing is overwritten
without your approval.

Run `./check.sh` to see which tools the harness expects — d2, task, jq,
pandoc — and how to install any that are missing. Missing tools disable
only the skills that need them.

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
