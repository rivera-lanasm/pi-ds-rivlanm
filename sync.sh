#!/bin/sh
# Sync this repo with the live pi harness. Copies, never symlinks.
#
#   ./sync.sh push    repo -> live   (deploy; run on a new machine)
#   ./sync.sh pull    live -> repo   (collect edits for git review)
#
# push replaces a live item only when it differs, and backs it up first.
# pull only touches items that already exist in the repo; it never adds
# new items, so a skill you want to keep private stays out of git.
#
# settings.json is special: defaultProvider, defaultModel, and theme are
# local choices. push keeps the live values; pull filters them out. jq
# must be installed.
set -eu

REPO="$(cd "$(dirname "$0")" && pwd)"
PI_AGENT="${PI_AGENT_DIR:-$HOME/.pi/agent}"
AGENTS_HOME="${AGENTS_HOME_DIR:-$HOME/.agents}"

mode="${1:-}"
[ "$mode" = "push" ] || [ "$mode" = "pull" ] || {
    echo "usage: $0 push|pull" >&2
    exit 2
}

# item <repo-relative-path> <live-absolute-path>
item() {
    rel="$1"
    live="$2"
    repo_path="$REPO/$rel"

    if [ "$mode" = "push" ]; then
        [ -e "$repo_path" ] || return 0
        src="$repo_path"
        tmp=""
        if [ "$rel" = "settings.json" ] && [ -e "$live" ]; then
            # Local choices win over the repo file.
            tmp="$(mktemp)"
            if ! jq -s '(.[1] | {defaultProvider, defaultModel, theme} | with_entries(select(.value != null))) as $keep | .[0] + $keep' \
                "$repo_path" "$live" > "$tmp"; then
                rm -f "$tmp"
                exit 1 # jq names the parse error on stderr
            fi
            src="$tmp"
        fi
        if [ -e "$live" ] && diff -rq "$src" "$live" >/dev/null 2>&1; then
            [ -z "$tmp" ] || rm -f "$tmp"
            return 0 # identical, nothing to do
        fi
        if [ -e "$live" ]; then
            mv "$live" "$live.bak.$(date +%Y%m%d%H%M%S)"
            echo "backed up $live"
        fi
        mkdir -p "$(dirname "$live")"
        cp -R "$src" "$live"
        [ -z "$tmp" ] || rm -f "$tmp"
        echo "pushed $rel"
    else
        # pull: only items the repo already tracks
        [ -e "$repo_path" ] && [ -e "$live" ] || return 0
        if [ "$rel" = "settings.json" ]; then
            # Write through a temp file: a jq error must not truncate the
            # tracked copy.
            tmp="$(mktemp)"
            if ! jq 'del(.defaultProvider, .defaultModel, .theme)' "$live" > "$tmp"; then
                rm -f "$tmp"
                exit 1 # jq names the parse error on stderr
            fi
            if diff -q "$tmp" "$repo_path" >/dev/null 2>&1; then
                rm -f "$tmp"
                return 0
            fi
            mv "$tmp" "$repo_path"
        else
            if diff -rq "$live" "$repo_path" >/dev/null 2>&1; then
                return 0
            fi
            rm -rf "$repo_path"
            cp -R "$live" "$repo_path"
        fi
        echo "pulled $rel"
    fi
}

# Tracked files and directories. A glob means: every entry the repo holds.
items() {
    item AGENTS.md "$PI_AGENT/AGENTS.md"
    item settings.json "$PI_AGENT/settings.json"
    item doc-preview-header.html "$PI_AGENT/doc-preview-header.html"

    for d in "$REPO"/skills/*/ "$REPO"/local/skills/*/; do
        [ -d "$d" ] || continue
        name="$(basename "$d")"
        item "${d#"$REPO"/}" "$PI_AGENT/skills/$name"
    done

    for f in "$REPO"/subagent-manager/agents/*; do
        [ -e "$f" ] || continue
        item "${f#"$REPO"/}" "$PI_AGENT/subagent-manager/agents/$(basename "$f")"
    done

    for d in "$REPO"/agents/skills/*/ "$REPO"/local/agents-skills/*/; do
        [ -d "$d" ] || continue
        item "${d#"$REPO"/}" "$AGENTS_HOME/skills/$(basename "$d")"
    done
}

items

if [ "$mode" = "pull" ]; then
    echo
    echo "Review with: git -C $REPO diff"
else
    echo
    echo "Secrets and state (auth.json, sessions/, npm/, models-store.json) untouched."
fi
