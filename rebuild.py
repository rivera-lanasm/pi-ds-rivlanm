#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Rebuild customized pi-subagent-manager agents after a version bump.

Each file in subagent-manager/agents/ that has a sibling in
subagent-manager/upstream/ is a customized copy of a shipped agent.
This script three-way merges it:

  base    subagent-manager/upstream/<name>.md   pristine, at the old pin
  yours   subagent-manager/agents/<name>.md     your customizations
  new     the installed package's agents/<name>.md, at the new pin

Run it after you bump the pin in settings.json and manifest.toml and run
`pi install npm:pi-subagent-manager@<new-pin>`. A clean merge refreshes
both agents/<name>.md and upstream/<name>.md. A conflict leaves markers
in agents/<name>.md for you to resolve; upstream/ is still refreshed, so
do not rerun the merge — edit the markers and commit.

Agents without an upstream/ sibling are fully custom and are skipped.
"""

import os
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent
PI_AGENT = Path(os.environ.get("PI_AGENT_DIR", Path.home() / ".pi" / "agent"))

MANIFEST = tomllib.loads((REPO / "manifest.toml").read_text())
PACKAGE = MANIFEST["packages"]["pi-subagent-manager"]["package"]
INSTALLED_AGENTS = PI_AGENT / "npm" / "node_modules" / PACKAGE / "agents"


def merge(ours: Path, base: Path, theirs: Path) -> subprocess.CompletedProcess:
    """Run git merge-file and return the completed process.

    stdout holds the merged text. The return code is the number of
    conflicts; git merge-file exits 255 with a message on stderr when it
    cannot run at all.
    """
    return subprocess.run(
        ["git", "merge-file", "-p", str(ours), str(base), str(theirs)],
        capture_output=True,
        text=True,
    )


def main() -> int:
    """Merge each customized agent. Returns 1 when any merge conflicts."""
    ours_dir = REPO / "subagent-manager" / "agents"
    base_dir = REPO / "subagent-manager" / "upstream"
    if not INSTALLED_AGENTS.is_dir():
        sys.exit(f"installed package not found at {INSTALLED_AGENTS}")

    conflicts = 0
    for ours in sorted(ours_dir.glob("*.md")):
        base = base_dir / ours.name
        if not base.exists():
            print(f"{ours.name}: fully custom, skipped")
            continue
        theirs = INSTALLED_AGENTS / ours.name
        if not theirs.exists():
            print(f"{ours.name}: no longer shipped upstream, skipped")
            continue
        if base.read_text() == theirs.read_text():
            print(f"{ours.name}: already at installed version")
            continue

        result = merge(ours, base, theirs)
        if result.returncode != 0 and result.stderr.strip():
            # A merge that cannot run leaves stdout empty. Write nothing.
            sys.exit(f"git merge-file failed for {ours.name}: {result.stderr.strip()}")
        ours.write_text(result.stdout)
        base.write_text(theirs.read_text())
        if result.returncode > 0:
            conflicts += 1
            print(
                f"{ours.name}: {result.returncode} conflict(s) — resolve markers in {ours}"
            )
        else:
            print(f"{ours.name}: merged cleanly")

    if conflicts == 0:
        print("\nReview with: git -C", REPO, "diff")
    return 1 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
