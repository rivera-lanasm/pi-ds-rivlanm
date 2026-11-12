#!/bin/bash
# Adoption test driver. Stands in for the adopting pi agent and follows
# ADOPT.md step by step, then asserts the outcome.
set -euo pipefail

PI_AGENT="$HOME/.pi/agent"
REPO="$HOME/pi-harness"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "  ok: $*"; }

echo "== 0. Fixture: a user with own skills, one collision, and own settings =="
mkdir -p "$PI_AGENT/skills/user-logs" "$PI_AGENT/skills/user-sql" \
         "$PI_AGENT/skills/code-standards" "$HOME/.agents/skills/user-broad"
for s in user-logs user-sql; do
    printf -- "---\nname: %s\ndescription: user-owned fixture skill\n---\n" "$s" \
        > "$PI_AGENT/skills/$s/SKILL.md"
done
printf -- "---\nname: code-standards\ndescription: the user's own code standards\n---\nUSER-MARKER\n" \
    > "$PI_AGENT/skills/code-standards/SKILL.md"
printf -- "---\nname: user-broad\ndescription: user-owned broad fixture skill\n---\n" \
    > "$HOME/.agents/skills/user-broad/SKILL.md"
printf '# My rules\n\n- The user works with CUDA kernels.\n- ANSWER-USER-MARKER\n' \
    > "$PI_AGENT/AGENTS.md"
cat > "$PI_AGENT/settings.json" <<'JSON'
{
  "lastChangelogVersion": "0.0.0",
  "theme": "light",
  "defaultProvider": "anthropic",
  "defaultModel": "claude-test-model",
  "packages": [
    "npm:user-own-extension"
  ]
}
JSON
echo '{"fixture":"secret"}' > "$PI_AGENT/auth.json"
AUTH_BEFORE="$(cat "$PI_AGENT/auth.json")"

echo "== 1. Clone and check the tools (ADOPT.md step 1) =="
git clone -q /src/pi-harness "$REPO"
if "$REPO/check.sh" > /tmp/check.out 2>&1; then
    fail "check.sh passed but the image lacks d2, task, pandoc"
fi
for tool in d2 task pandoc; do
    grep -q "MISSING: $tool " /tmp/check.out || fail "check.sh did not flag $tool"
done
grep -q "ok:      git" /tmp/check.out || fail "check.sh did not confirm git"
grep -q "ok:      jq" /tmp/check.out || fail "check.sh did not confirm jq"
ok "check.sh flags missing tools and confirms present ones"

echo "== 2. Pick the skills (step 2): keep the user's code-standards, install the rest =="
for d in "$REPO"/skills/*/; do
    name="$(basename "$d")"
    [ "$name" = "code-standards" ] && continue # collision: the user keeps theirs
    cp -r "$d" "$PI_AGENT/skills/$name"
done

echo "== 3. Adopt the global AGENTS.md (step 3): combine, lose nothing =="
cp "$REPO/AGENTS.md" "$PI_AGENT/AGENTS.md"
cat >> "$PI_AGENT/AGENTS.md" <<'EOF'

## Rules from the existing AGENTS.md

- The user works with CUDA kernels.
- ANSWER-USER-MARKER
EOF
grep -q "ANSWER-USER-MARKER" "$PI_AGENT/AGENTS.md" \
    || fail "combining lost the user's AGENTS.md content"
grep -q "| \`workspace\` |" "$PI_AGENT/AGENTS.md" \
    || fail "combined AGENTS.md lacks the repo routing table"
ok "AGENTS.md combined: user rules kept, repo routing table added"

echo "== 4. Merge the settings (step 4) =="
cp "$PI_AGENT/settings.json" "$PI_AGENT/settings.json.bak"
jq -s '
  (.[1] | {defaultProvider, defaultModel, theme} | with_entries(select(.value != null))) as $local
  | (.[0].packages // []) as $repo_pkgs
  | (.[1].packages // []) as $live_pkgs
  | .[1] + .[0] + $local
  | .packages = ($repo_pkgs + ($live_pkgs | map(select(
      . as $p | ($repo_pkgs | map(split("@")[0]) | index($p | split("@")[0])) | not))))
' "$REPO/settings.json" "$PI_AGENT/settings.json" > /tmp/settings.merged
mv /tmp/settings.merged "$PI_AGENT/settings.json"

echo "== 5. Install the extensions (step 5) =="
PKG="$(jq -r '.packages[] | select(contains("pi-subagent-manager"))' "$PI_AGENT/settings.json")"
pi install "$PKG"

echo "== 6. Install the custom agents and the render header (step 6) =="
mkdir -p "$PI_AGENT/subagent-manager/agents"
cp "$REPO"/subagent-manager/agents/*.md "$PI_AGENT/subagent-manager/agents/"
cp "$REPO"/doc-preview-header.html "$PI_AGENT/doc-preview-header.html"

echo "== Assertions =="
[ -d "$PI_AGENT/skills/user-logs" ] && [ -d "$PI_AGENT/skills/user-sql" ] \
    || fail "user skills missing from live"
[ -d "$HOME/.agents/skills/user-broad" ] || fail "user broad skill missing"
ok "user skills untouched in the live directories"
grep -q USER-MARKER "$PI_AGENT/skills/code-standards/SKILL.md" \
    || fail "collision: the user's code-standards was overwritten"
ok "same-name collision resolved: the user's version stays"
[ -d "$PI_AGENT/skills/simple-english" ] || fail "repo skills missing"
ok "picked repo skills installed"
[ "$(cat "$PI_AGENT/auth.json")" = "$AUTH_BEFORE" ] || fail "auth.json changed"
ok "auth.json untouched"
jq -e '
  .defaultProvider == "anthropic" and .theme == "light"
  and (.packages | index("npm:pi-subagent-manager@0.25.0") != null)
  and (.packages | index("npm:user-own-extension") != null)
' "$PI_AGENT/settings.json" > /dev/null || fail "settings merge wrong"
ok "settings keep the user keys, the user extensions, and the repo pin"
[ -f "$PI_AGENT/subagent-manager/agents/ws-coder.md" ] || fail "ws-coder.md missing"
[ -f "$PI_AGENT/subagent-manager/agents/ws-architect.md" ] || fail "ws-architect.md missing"
[ -f "$PI_AGENT/subagent-manager/agents/ws-researcher.md" ] || fail "ws-researcher.md missing"
for f in "$PI_AGENT"/subagent-manager/agents/ws-*.md; do
    icon="$(sed -n "s/^icon: '\(.*\)'$/\1/p" "$f")"
    printf '%s' "$icon" | LC_ALL=C.UTF-8 grep -qP '^\p{Co}$' \
        || fail "$(basename "$f"): icon is not a single private-use glyph; the extension drops the agent"
done
ok "custom agents (ws-coder, ws-architect, ws-researcher) installed with valid icons"
[ -d "$PI_AGENT/npm/node_modules/pi-subagent-manager" ] \
    || fail "pi-subagent-manager not installed"
ok "pi-subagent-manager installed at the pinned version"
cd "$REPO"
[ -z "$(git status --porcelain)" ] \
    || fail "repo dirty after adoption: $(git status --porcelain)"
ok "repo git tree clean"
jq -e '(has("defaultProvider") or has("defaultModel")) | not' settings.json > /dev/null \
    || fail "repo settings.json not provider-neutral"
ok "repo settings.json carries no provider or model"

echo
echo "== 7. Happy path: one ticket's full life in a workspace =="
apt-get update >/dev/null 2>&1
apt-get install -y --no-install-recommends taskwarrior pandoc >/dev/null 2>&1
mkdir -p /root/.task
printf 'data.location=/root/.task\n' > /root/.taskrc
WS=/tmp/ws-happy
"$REPO/skills/workspace/scripts/tw-check.py" --init "$WS" >/dev/null
printf 'project = "happy"\n' > "$WS/workspace.toml"
sed -i 's/^Project: .*/Project: happy/' "$WS/AGENTS.md"
UUID="$(cat <<'JSON' | "$REPO/skills/workspace/scripts/tw-new.py"
{
  "title": "Prove the happy path in the container",
  "project": "happy.path",
  "tags": ["test"],
  "depends": [],
  "problem": ["The happy path of the workspace is unproven in a container"],
  "decision": ["Run one ticket through its full life"],
  "artifacts": ["One closed ticket with a conclusion document"],
  "risks": [{"risk": "A script fails in the container", "detection": "A command exits non-zero"}],
  "done_when": ["The ticket is closed and annotated"]
}
JSON
)"
[ -n "$UUID" ] || fail "tw-new.py created no ticket"
ok "tw-new.py created ticket ${UUID:0:8}"
task rc.verbose=nothing project:happy.path export | jq -e 'length == 1' >/dev/null \
    || fail "ticket not in the task database"
ok "ticket lives in the task database"
TICKET_ID="${UUID:0:8}"
cat > "$WS/conclusions/$TICKET_ID.md" <<MD
# $TICKET_ID: Prove the happy path

Ticket: $UUID
Status: done

## Goal

- Prove the happy path.

## Progress

- Created the ticket. Closed it in the container.

## Done

- The ticket is closed with this document.

## Decisions

- One ticket proves the loop.

## Artifacts

- conclusions/$TICKET_ID.md

## Open items

- None
MD
"$REPO/skills/workspace/scripts/tw-close.py" "$UUID" "$WS/conclusions/$TICKET_ID.md" >/dev/null \
    || fail "tw-close.py failed"
ok "tw-close.py linked the conclusion document"
printf '# Proposal %s\n\nOne design, proved in a container.\n' "$TICKET_ID" \
    > "$WS/proposals/$TICKET_ID.md"
"$REPO/skills/workspace/scripts/render.sh" "$WS/proposals/$TICKET_ID.md" >/dev/null
[ -f "$WS/proposals/$TICKET_ID.html" ] || fail "render produced no HTML"
grep -q "sourceCode.diff" "$WS/proposals/$TICKET_ID.html" \
    || fail "render HTML lacks the harness header styles"
ok "render produced styled HTML for the proposal document"
"$REPO/skills/workspace/scripts/tw-check.py" "$WS" | tail -1 | grep -q "0 errors" \
    || fail "tw-check.py reported errors on the happy workspace"
ok "tw-check.py reports zero errors on the workspace"

echo
echo "== 8. brief-new.py: the briefs that start the ws- agents =="
git init -q "$WS/repos/notes-app"
printf 'project = "happy"\n\n[repos]\nwork = ["notes-app"]\n' > "$WS/workspace.toml"
BRIEF="$REPO/skills/workspace/scripts/brief-new.py"
"$BRIEF" --schema ws-researcher > /dev/null || fail "--schema ws-researcher failed"
RESEARCHER_BRIEF="$($BRIEF ws-researcher <<JSON
{
  "workspace": "$WS",
  "question": "How does the workspace ticket flow work end to end",
  "document": "auth-1.md",
  "context": ["The workspace skill in the harness repo"]
}
JSON
)" || fail "brief-new.py rejected a valid researcher brief"
printf '%s' "$RESEARCHER_BRIEF" | grep -q "Question: How does the workspace ticket flow" \
    || fail "the researcher brief does not carry the question"
ok "ws-researcher brief: validated against the workspace and rendered"
ARCHITECT_BRIEF="$($BRIEF ws-architect <<JSON
{
  "workspace": "$WS",
  "ticket": "$UUID",
  "work_repos": ["notes-app"]
}
JSON
)" || fail "brief-new.py rejected a valid architect brief"
printf '%s' "$ARCHITECT_BRIEF" | grep -q "Ticket: $TICKET_ID" \
    || fail "the architect brief does not carry the ticket"
printf '%s' "$ARCHITECT_BRIEF" | grep -q "Title: Prove the happy path in the container" \
    || fail "the architect brief does not carry the ticket title"
ok "ws-architect brief: read the ticket and rendered its title"
if printf '%s' '{"workspace": "'"$WS"'", "question": "Two sentences. This one too.", "document": "x-1.md", "context": ["The repo"]}' \
    | "$BRIEF" ws-researcher 2>/tmp/brief.err; then
    fail "brief-new.py accepted a two-sentence question"
fi
grep -q "more than one sentence" /tmp/brief.err || fail "wrong error for the two-sentence question"
touch "$WS/research/auth-1.md"
if "$BRIEF" ws-researcher <<JSON 2>/tmp/brief.err
{
  "workspace": "$WS",
  "question": "How does the workspace ticket flow work end to end",
  "document": "auth-1.md",
  "context": ["The workspace skill in the harness repo"]
}
JSON
then
    fail "brief-new.py accepted an existing document"
fi
grep -q "already exists" /tmp/brief.err || fail "wrong error for the existing document"
if printf '%s' '{"workspace": "'"$WS"'", "question": "Fork without a parent", "document": "bug-2.1.md", "context": ["The repo"]}' \
    | "$BRIEF" ws-researcher 2>/tmp/brief.err; then
    fail "brief-new.py accepted a fork without its parent document"
fi
grep -q "a fork needs its parent" /tmp/brief.err || fail "wrong error for the parentless fork"
ok "brief-new.py rejects: two-sentence question, existing document, parentless fork"

echo
echo "ADOPTION TEST PASSED"
