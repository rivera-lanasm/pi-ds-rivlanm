#!/usr/bin/env -S uv run --script
"""Check external components against upstream and show diffs.

Reads manifest.toml. Changes nothing in this repo or on the system.
After you review a diff, apply updates by hand:

- npm package: bump the pin in settings.json and manifest.toml, then run
  `pi update --extensions`.
- git skill: merge the upstream changes into skills/<name>, then set
  `base` in manifest.toml to the new upstream commit.

Usage:
    uv run update.py             # report status of every component
    uv run update.py <name>      # show upstream log and diff for one component
"""

import json
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent
MANIFEST = tomllib.loads((REPO / "manifest.toml").read_text())

COMPONENTS = {}
for group_name in ("packages", "skills"):
    for name, section in MANIFEST.get(group_name, {}).items():
        COMPONENTS[name] = section | {"group": group_name}


def run(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, check=True
    ).stdout.strip()


def npm_status(name: str, section: dict) -> str:
    latest = run("npm", "view", section["package"], "version")
    pin = section["pin"]
    state = "current" if pin == latest else f"behind (upstream {latest})"
    line = f"{name}: pinned {pin}, {state}"
    expected = f"npm:{section['package']}@{pin}"
    settings = json.loads((REPO / "settings.json").read_text())
    if expected not in settings.get("packages", []):
        line += f" — WARNING: settings.json lacks {expected!r} (a pull may have stripped it)"
    return line


def npm_detail(name: str, section: dict) -> str:
    changelog = run("npm", "view", section["package"], "--json", "time")
    published = json.loads(changelog)
    pin = section["pin"]
    newer = sorted(
        (v for v in published if v not in ("created", "modified")),
    )
    newer = newer[newer.index(pin) + 1 :] if pin in newer else newer
    lines = [f"Versions after your pin {pin}: {', '.join(newer) or 'none'}"]
    lines.append("Bump the pin in settings.json and manifest.toml, then run:")
    lines.append(f"    pi install npm:{section['package']}@<new-pin>")
    return "\n".join(lines)


def git_clone(url: str, work: Path) -> Path:
    dest = work / "upstream"
    run("git", "clone", "--quiet", url, str(dest))
    return dest


def git_status(name: str, section: dict) -> str:
    with tempfile.TemporaryDirectory() as work:
        clone = git_clone(section["url"], Path(work))
        head = run("git", "rev-parse", "HEAD", cwd=clone)
        base = section["base"]
        if head == base:
            return f"{name}: at recorded base {base[:8]}, current"
        count = run("git", "rev-list", "--count", f"{base}..HEAD", cwd=clone)
        return f"{name}: {count} upstream commit(s) since base {base[:8]}"


def git_detail(name: str, section: dict) -> str:
    ours = REPO / "skills" / name
    lines = []
    with tempfile.TemporaryDirectory() as work:
        clone = git_clone(section["url"], Path(work))
        base, head = section["base"], run("git", "rev-parse", "HEAD", cwd=clone)
        lines.append(f"Upstream log {base[:8]}..{head[:8]}:")
        log = run(
            "git", "log", "--oneline", f"{base}..{head}", cwd=clone
        )
        lines.append(log or "  (no new commits)")
        upstream_path = clone / section["path"]
        if head != base:
            lines.append("\nUpstream changes to this skill since base:")
            diff = run(
                "git", "diff", base, head, "--", section["path"], cwd=clone
            )
            lines.append(diff or "  (skill directory untouched)")
        lines.append(f"\nDiff of upstream HEAD vs your copy skills/{name}:")
        diff = subprocess.run(
            ["diff", "-ru", str(upstream_path), str(ours)],
            capture_output=True, text=True,
        ).stdout
        lines.append(diff or "  (identical)")
    lines.append(
        "\nTo update: merge upstream changes into "
        f"skills/{name}, then set base = \"{head}\" in manifest.toml."
    )
    return "\n".join(lines)


def main() -> None:
    args = sys.argv[1:]
    if args:
        name = args[0]
        if name not in COMPONENTS:
            known = ", ".join(sorted(COMPONENTS))
            sys.exit(f"unknown component {name!r}; known: {known}")
        section = COMPONENTS[name]
        detail = npm_detail if section["type"] == "npm" else git_detail
        print(detail(name, section))
        return
    for name, section in COMPONENTS.items():
        status = npm_status if section["type"] == "npm" else git_status
        try:
            print(status(name, section))
        except subprocess.CalledProcessError as exc:
            print(f"{name}: check failed: {exc.stderr.strip()}")


if __name__ == "__main__":
    main()
