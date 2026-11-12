#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Rebuild customized pi-subagent-manager agents after a version bump.

Each file subagent-manager/agents/ws-<name>.md is a fork of the shipped
agent <name>. The ws- prefix makes the fork a separate agent type, so it
does not replace the shipped one. A fork has its pristine shipped copy
in subagent-manager/upstream/<name>.md. This script three-way merges it:

  base    subagent-manager/upstream/<name>.md   pristine, at the old pin
  yours   subagent-manager/agents/ws-<name>.md  your customizations
  new     the installed package's agents/<name>.md, at the new pin

Run it after you bump the pin in settings.json and manifest.toml and run
`pi install npm:pi-subagent-manager@<new-pin>`. A clean merge refreshes
both agents/ws-<name>.md and upstream/<name>.md. A conflict leaves
markers in agents/ws-<name>.md for you to resolve; upstream/ is still
refreshed, so do not rerun the merge — edit the markers and commit.

Agents without an upstream/ copy are fully custom and are skipped.
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

# Filename prefix of a fork: agents/ws-coder.md forks the shipped coder.md.
FORK_PREFIX = "ws-"


def shipped_name(fork_name: str) -> str:
    """Return the filename of the shipped agent that a fork derives from.

    `fork_name` is a filename such as "ws-coder.md". A name without the
    prefix returns unchanged: such a file overrides the shipped agent of
    the same name.
    """
    return fork_name.removeprefix(FORK_PREFIX)


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
        shipped = shipped_name(ours.name)
        base = base_dir / shipped
        if not base.exists():
            print(f"{ours.name}: fully custom, skipped")
            continue
        theirs = INSTALLED_AGENTS / shipped
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
