# Adopt this harness

Guidance for the pi agent on the new machine. The user has pi installed
and may have skills of their own. The goal: this repo becomes the primary
harness, and the user's own skills keep working without entering git.

## Prerequisites

- pi is installed and the user is logged in (`~/.pi/agent` exists)
- after the clone in step 1, run `./check.sh` — it lists every tool the
  harness expects, names what is missing, and gives the install command.
  Missing tools only disable the skills that need them; they do not
  block adoption.

## 1. Clone

```sh
git clone https://github.com/rivera-lanasm/pi-ds-rivlanm.git ~/pi-harness
```

## 2. Move the user's skills into `local/`

For each directory in `~/.pi/agent/skills/` that this repo does **not**
provide (compare names with `~/pi-harness/skills/`):

```sh
mv ~/.pi/agent/skills/<name> ~/pi-harness/local/skills/<name>
```

For each directory in `~/.agents/skills/` that this repo does not provide:

```sh
mv ~/.agents/skills/<name> ~/pi-harness/local/agents-skills/<name>
```

If a name collides with a repo skill, stop and ask the user which one to
keep.

Why: `local/` is gitignored. Skills there sync to the live system through
`sync.sh` and never appear in `git status`.

## 3. Deploy

```sh
cd ~/pi-harness && ./sync.sh push
```

`push` backs up every live file it replaces (`*.bak.<timestamp>` next to
the original). List the backups for the user when it finishes.

## 4. Re-apply the user's settings

`push` replaced `~/.pi/agent/settings.json`; `auth.json` was not touched.
Read the backup and re-apply the user-specific keys: `defaultProvider`,
`defaultModel`, `theme`.

Merge the `packages` lists too: keep every entry from the backup and from
the repo. On overlap, the repo's pinned entry wins. This preserves the
user's own extensions next to the pinned pi-subagent-manager. Their
installed files are still on disk; the settings entry is what pi loads.

The repo's `settings.json` carries no provider or model. When the user
changes provider later — together, LiteLLM, or another — `sync.sh pull`
filters `defaultProvider` and `defaultModel` out, so the choice stays
local and never enters git.

## 5. Install the pinned extension

Run `pi install` with each entry in the `packages` list in
`~/.pi/agent/settings.json`:

```sh
pi install npm:pi-subagent-manager@0.25.0
```

`pi update --extensions` is not enough here: it updates installed packages
but skips a pinned package that is not installed yet. The pin survives
later `pi update --extensions` runs. The repo's custom agents (coder and
architect) are already in place from step 3.

## 6. Verify

- pi starts without errors
- the user's skills are listed and work (they now live under `local/`,
  synced to the live locations)
- pi-subagent-manager loads with the repo's coder agent

## Day to day

- Add a skill: put it in `local/skills/` (or `local/agents-skills/` for
  the broad directory) and run `sync.sh push`. Git never sees it.
- A skill dropped straight into `~/.pi/agent/skills/` also stays out of
  the repo — `sync.sh pull` never adds new items. Prefer `local/` so the
  skill lives with the working tree.
- Edit a tracked file during a session: `./sync.sh pull` collects it, then
  review with `git diff`.
