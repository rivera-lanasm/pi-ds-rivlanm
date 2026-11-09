#!/bin/bash
# Adoption test driver. Stands in for the local pi agent and follows
# ADOPT.md step by step, then asserts the outcome.
set -euo pipefail

PI_AGENT="$HOME/.pi/agent"
REPO="$HOME/pi-harness"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "  ok: $*"; }

echo "== 0. Fixture: a user who already runs pi, with 3 own skills =="
mkdir -p "$PI_AGENT/skills/user-logs" "$PI_AGENT/skills/user-sql" \
         "$HOME/.agents/skills/user-broad"
for s in user-logs user-sql; do
    printf -- "---\nname: %s\ndescription: user-owned fixture skill\n---\n" "$s" \
        > "$PI_AGENT/skills/$s/SKILL.md"
done
printf -- "---\nname: user-broad\ndescription: user-owned broad fixture skill\n---\n" \
    > "$HOME/.agents/skills/user-broad/SKILL.md"
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

echo "== 1. Clone (ADOPT.md step 1) =="
git clone -q /src/pi-harness "$REPO"
mkdir -p "$REPO/local/skills" "$REPO/local/agents-skills"

echo "== 2. Move the user's skills into local/ (step 2) =="
mv "$PI_AGENT/skills/user-logs" "$PI_AGENT/skills/user-sql" "$REPO/local/skills/"
mv "$HOME/.agents/skills/user-broad" "$REPO/local/agents-skills/"

echo "== 3. Deploy (step 3) =="
"$REPO/sync.sh" push

echo "== 4. Re-apply the user's settings (step 4) =="
BACKUP="$(ls -d "$PI_AGENT"/settings.json.bak.* | head -1)"
[ -n "$BACKUP" ] || fail "no settings.json backup found"
node -e '
const fs = require("fs");
const [backupPath, livePath] = process.argv.slice(1);
const backup = JSON.parse(fs.readFileSync(backupPath, "utf8"));
const live = JSON.parse(fs.readFileSync(livePath, "utf8"));
for (const k of ["defaultProvider", "defaultModel", "theme"]) {
    if (k in backup) live[k] = backup[k];
}
const merged = [...(live.packages || [])];
for (const p of backup.packages || []) {
    if (!merged.some(q => q.split("@")[0] === p.split("@")[0])) merged.push(p);
}
live.packages = merged;
fs.writeFileSync(livePath, JSON.stringify(live, null, 2) + "\n");
' "$BACKUP" "$PI_AGENT/settings.json"

echo "== 5. Install the pinned extension (step 5) =="
PKG="$(node -e 'console.log(JSON.parse(require("fs").readFileSync(process.argv[1], "utf8")).packages.find(p => p.includes("pi-subagent-manager")))' "$PI_AGENT/settings.json")"
pi install "$PKG"

echo "== 6. Dependency check =="
if "$REPO/check.sh" > /tmp/check.out 2>&1; then
    fail "check.sh passed but the image lacks d2, logseq, task, jq, ruff"
fi
for tool in d2 logseq task jq ruff; do
    grep -q "MISSING: $tool " /tmp/check.out || fail "check.sh did not flag $tool"
done
grep -q "ok:      git" /tmp/check.out || fail "check.sh did not confirm git"
ok "check.sh flags missing tools and confirms present ones"

echo "== Assertions =="
[ -d "$PI_AGENT/skills/user-logs" ] && [ -d "$PI_AGENT/skills/user-sql" ] \
    || fail "user skills missing from live"
ok "user skills present in live ~/.pi/agent/skills"
[ -d "$HOME/.agents/skills/user-broad" ] || fail "user broad skill missing"
ok "user broad skill present in live ~/.agents/skills"
[ -d "$PI_AGENT/skills/simple-english" ] || fail "repo skills missing"
ok "repo skills deployed"
[ "$(cat "$PI_AGENT/auth.json")" = "$AUTH_BEFORE" ] || fail "auth.json changed"
ok "auth.json untouched"
node -e '
const s = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"));
if (s.defaultProvider !== "anthropic") throw new Error("provider lost");
if (s.theme !== "light") throw new Error("theme lost");
if (!(s.packages || []).includes("npm:pi-subagent-manager@0.25.0"))
    throw new Error("pin lost");
if (!(s.packages || []).includes("npm:user-own-extension"))
    throw new Error("user extension dropped");
' "$PI_AGENT/settings.json" || fail "settings.json wrong"
ok "settings.json keeps user settings, user extensions, and the repo pin"
[ -f "$PI_AGENT/subagent-manager/agents/coder.md" ] || fail "coder.md missing"
ok "custom coder agent deployed"
[ -d "$PI_AGENT/npm/node_modules/pi-subagent-manager" ] \
    || fail "pi-subagent-manager not installed"
ok "pi-subagent-manager installed at the pinned version"
cd "$REPO"
[ -z "$(git status --porcelain)" ] \
    || fail "repo dirty after adoption: $(git status --porcelain)"
ok "repo git tree clean: user skills and settings stayed out of git"

echo
echo "ADOPTION TEST PASSED"
