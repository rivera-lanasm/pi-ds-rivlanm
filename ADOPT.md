# Adopt this harness

Guidance for the pi agent on the new machine. The user runs pi and can
have skills and extensions of their own. You install the parts of this
harness that the user picks. Nothing overwrites a skill or an extension
of the user without the approval of the user.

## Prerequisites

- pi is installed and the user is logged in (`~/.pi/agent` exists)
- git, uv, and jq are installed

## 1. Clone and check the tools

```sh
git clone https://github.com/rivera-lanasm/pi-ds-rivlanm.git ~/pi-harness
~/pi-harness/check.sh
```

`check.sh` lists every tool the harness expects and gives the install
command for each missing one. Install what is missing, or skip the
skills that need it.

## 2. Pick the product, then the skills

The harness holds two products. "What the harness gives you" in
`README.md` describes them. Show the user that section. Then ask the
user which product to adopt:

- **The standards alone.** Five skills: `code-standards`,
  `testing-standards`, `simple-english`, `d2-diagrams`, and `show-me`.
  Do steps 2, 3, and 7. Skip steps 4, 5, and 6.
- **The standards and the workflow.** The five skills, plus the
  `workspace` skill, the `socratic-review` skill, the pinned extension,
  and the custom agents. Do every step.

The workflow reads the standards, so there is no choice of the workflow
alone.

List the skills of the chosen product (`~/pi-harness/skills/`) next to
the skills of the user (`~/.pi/agent/skills/`).

- A name in both lists is a collision. Show the user the diff. If the
  user wants the version of the repo, replace the skill. If the user
  wants to keep their version, do nothing.
- A skill that exists only in the repo needs the approval of the user.
  Copy each skill the user picks. When the target already exists, remove
  it first: `cp -r` into an existing directory nests the copy, and the
  old version stays active.

```sh
rm -rf ~/.pi/agent/skills/<name>
cp -r ~/pi-harness/skills/<name> ~/.pi/agent/skills/<name>
```

If the user adopts the workflow and declines a standard, name the part
that reads it. The table in "The workflow" in `README.md` gives the
parts.

Skills of the user that the repo does not provide stay where they are.
No step in this guide removes them.

## 3. Adopt the global AGENTS.md

`AGENTS.md` holds the global instructions: the working rules and the
skills table. It is the keystone of the harness.

- When the user has no `~/.pi/agent/AGENTS.md`, copy the file of the
  repo.
- When the user has one, combine the two. Read both files. Keep every
  rule and every section of the user. Add the rules and the skills
  table of the repo that the user does not already have. In the skills
  table, keep only the rows of the skills that the user installed. When
  two rules conflict, show the user both rules and let the user decide. The
  content of the user is never dropped.
- Show the user the combined file. Adopt it when the user approves.

## 4. Merge the settings (workflow only)

If the user adopted the standards alone, skip this step. The settings
of the repo exist to pin the extension of the workflow.

If `~/.pi/agent/settings.json` exists, merge it with the file of the
repo. The repo file wins, except three local keys (`defaultProvider`,
`defaultModel`, `theme`). The `packages` lists merge, and the entry of
the repo wins per package name:

```sh
cp ~/.pi/agent/settings.json ~/.pi/agent/settings.json.bak
jq -s '
  (.[1] | {defaultProvider, defaultModel, theme} | with_entries(select(.value != null))) as $local
  | (.[0].packages // []) as $repo_pkgs
  | (.[1].packages // []) as $live_pkgs
  | .[0] + $local
  | .packages = ($repo_pkgs + ($live_pkgs | map(select(
      . as $p | ($repo_pkgs | map(split("@")[0]) | index($p | split("@")[0])) | not))))
' ~/pi-harness/settings.json ~/.pi/agent/settings.json > /tmp/settings.merged \
  && mv /tmp/settings.merged ~/.pi/agent/settings.json
```

If the file does not exist yet, copy the file of the repo instead. In
both cases, `auth.json` is never touched.

## 5. Install the extensions (workflow only)

Run `pi install` with each entry in the `packages` list of the merged
`~/.pi/agent/settings.json`:

```sh
pi install npm:pi-subagent-manager@0.25.0
```

`pi update --extensions` is not enough here: it updates installed
packages but skips a pinned package that is not installed yet. The pin
survives later `pi update --extensions` runs.

## 6. Install the custom agents (workflow only)

When a file of that name already exists in
`~/.pi/agent/subagent-manager/agents/`, show the user the diff and ask
before you replace it. The user may have their own override for the same
agent.

```sh
mkdir -p ~/.pi/agent/subagent-manager/agents
cp ~/pi-harness/subagent-manager/agents/*.md ~/.pi/agent/subagent-manager/agents/
```

These are the customized coder, architect, and researcher. They replace
the shipped definitions of the same name. The pristine shipped copies
stay in `subagent-manager/upstream/` as merge bases for `rebuild.py`.

The render header styles the HTML renders of workspace documents. When
one already exists, show the user the diff and ask first:

```sh
cp ~/pi-harness/doc-preview-header.html ~/.pi/agent/doc-preview-header.html
```

## 7. Verify

- pi starts without errors
- the skills of the user and the picked skills of the repo are listed
- if the user adopted the workflow, pi-subagent-manager loads with the
  custom coder, architect, and researcher

## Day to day

- The skills of the user live in `~/.pi/agent/skills/`. Nothing in this
  repo collects them or removes them.
- To update a harness file, edit the repo copy. Then copy it into place.
- To update an external part, follow "Update an external part" in
  `README.md`.
