#!/bin/sh
# Check for the tools this harness expects. Prints an install hint for
# each missing one. Exit 0 when all are present, 1 otherwise.
set -u

missing=0

check() {
    cmd="$1"
    needed_by="$2"
    hint="$3"
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "ok:      $cmd"
    else
        missing=$((missing + 1))
        echo "MISSING: $cmd — needed by $needed_by"
        echo "         install: $hint"
    fi
}

echo "Core tooling:"
check pi   "the agent itself"                   "npm install -g @earendil-works/pi-coding-agent"
check git  "repo operations"                    "your package manager"
check uv   "update.py, rebuild.py, taskwarrior scripts" "curl -LsSf https://astral.sh/uv/install.sh | sh"
check node "pi itself"                          "https://nodejs.org"
check npm  "pi package installs"                "installed with node"
check rg   "pi file search"                     "your package manager (ripgrep)"

echo
echo "Skill dependencies:"
check task   "taskwarrior skill"  "https://taskwarrior.org/download/"
check jq     "taskwarrior skill"  "your package manager"
check d2     "d2-diagrams skill"  "curl -fsSL https://d2lang.com/install.sh | sh -s --"
check pandoc "taskwarrior skill (proposal documents)" "https://pandoc.org/installing.html"
check ruff   "code-standards skill (Python work)" "uv tool install ruff"

echo
if [ "$missing" -eq 0 ]; then
    echo "All expected tools are present."
else
    echo "$missing tool(s) missing. The harness runs without them; only"
    echo "the named skills or scripts lose function."
    exit 1
fi
