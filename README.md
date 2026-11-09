# pi-harness

This repo recreates the pi coding-agent harness on a new machine. It holds
the configuration, the skills, and the record of where each external part
came from.

## Layout

| Path | Synced to | Contents |
|---|---|---|
| `AGENTS.md`, `settings.json`, `doc-preview-header.html` | `~/.pi/agent/` | Global instructions and pi settings |
| `skills/` | `~/.pi/agent/skills/` | All skills, ours and vendored |
| `local/skills/`, `local/agents-skills/` | `~/.pi/agent/skills/`, `~/.agents/skills/` | Private skills. Gitignored, never committed |
| `subagent-manager/agents/` | `~/.pi/agent/subagent-manager/agents/` | Customized agents for pi-subagent-manager |
| `subagent-manager/upstream/` | — | Pristine shipped agents at the pinned version. Merge base for rebuilds |
| `agents/skills/` | `~/.agents/skills/` | Skills in the shared agents directory |
| `manifest.toml` | — | Source and pinned version of each external part |
| `sync.sh` | — | Copies between repo and live system, both ways |
| `update.py` | — | Checks pins against upstream and shows diffs |
| `rebuild.py` | — | Re-applies agent customizations after a package update |

## Install on a new machine

```sh
git clone <this-repo> ~/pi-harness
~/pi-harness/sync.sh push
```

If the machine already runs pi and has skills of its own, see `ADOPT.md` —
it moves the existing skills into `local/` before the first push.

`push` copies the repo into the live locations. It backs up a live file
before it replaces one that differs. It does not touch secrets or state:
`auth.json`, `sessions/`, `npm/`, `models-store.json` stay where they are.

Install pi itself and log in before or after; this repo does not manage
that.

## Keep repo and live system in step

The live system is a copy, not a link. Edits in one side do not appear in
the other until you sync:

```sh
./sync.sh pull    # live -> repo, then review with git diff
./sync.sh push    # repo -> live
```

`pull` only touches items the repo already has. It never adds new items,
so a skill that must stay out of git is never collected.

## Add a private skill

Put the skill directory in `local/skills/` (or `local/agents-skills/` for
the broad `~/.agents` directory) and run `sync.sh push`. Git ignores
`local/`, so the skill works on this machine and never enters the repo.

## Update an external part

```sh
uv run update.py                   # status of every external part
uv run update.py show-me           # upstream log and diffs for one part
```

`update.py` changes nothing. After you review a diff:

- **git skill** (`show-me`): merge the upstream changes into
  `skills/<name>`, then set `base` in `manifest.toml` to the new upstream
  commit. It carries a local modification; the diffs show upstream changes
  and our changes separately. `simple-english` was once tracked this way
  but is now our own skill; see the note in `manifest.toml`.
- **npm package** (`pi-subagent-manager`):
  1. Bump the pin in `settings.json` and `manifest.toml`.
  2. Run `pi install npm:pi-subagent-manager@<new-pin>` (an install, not
     `pi update --extensions`, which skips pinned packages it has not
     installed).
  3. Run `uv run rebuild.py`. It three-way merges each customized agent
     in `subagent-manager/agents/` against the newly installed version,
     using `subagent-manager/upstream/` as the base. Conflicts leave
     markers for manual resolution.
  4. Review with `git diff`, then `sync.sh push`.

## What is not in this repo, and why

- `auth.json` — credentials.
- `sessions/`, `models-store.json`, `npm/`, `subagent-manager/.import-offered`
  — state that pi regenerates.
- `bin/rg` — a binary. Install ripgrep through your package manager.
- `settings.json` has no secrets, so it is tracked.
