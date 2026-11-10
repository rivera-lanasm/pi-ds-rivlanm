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

## 2. Pick the skills

List the skills of the repo (`~/pi-harness/skills/`) next to the skills
of the user (`~/.pi/agent/skills/`).

- A name in both lists is a collision. Show the user the diff. If the
  user wants the version of the repo, copy it over. If the user wants to
  keep their version, do nothing.
- A skill that exists only in the repo needs the approval of the user.
  Copy each skill the user picks:

```sh
cp -r ~/pi-harness/skills/<name> ~/.pi/agent/skills/<name>
```

Skills of the user that the repo does not provide stay where they are.
No step in this guide removes them.

## 3. Merge the settings

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

## 4. Install the extensions

Run `pi install` with each entry in the `packages` list of the merged
`~/.pi/agent/settings.json`:

```sh
pi install npm:pi-subagent-manager@0.25.0
```

`pi update --extensions` is not enough here: it updates installed
packages but skips a pinned package that is not installed yet. The pin
survives later `pi update --extensions` runs.

## 5. Install the custom agents

```sh
mkdir -p ~/.pi/agent/subagent-manager/agents
cp ~/pi-harness/subagent-manager/agents/*.md ~/.pi/agent/subagent-manager/agents/
```

These are the customized coder and architect. They replace the shipped
definitions of the same name. The pristine shipped copies stay in
`subagent-manager/upstream/` as merge bases for `rebuild.py`.

## 6. Verify

- pi starts without errors
- the skills of the user and the picked skills of the repo are listed
- pi-subagent-manager loads with the custom coder and architect

## Day to day

- The skills of the user live in `~/.pi/agent/skills/`. Nothing in this
  repo collects them or removes them.
- To update a harness file, edit the repo copy. Then copy it into place.
- To update an external part, follow "Update an external part" in
  `README.md`.
