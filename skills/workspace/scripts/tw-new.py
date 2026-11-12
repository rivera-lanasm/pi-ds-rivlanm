#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pydantic>=2.7,<3"]
# ///
"""Create one Taskwarrior task from a validated ticket.

Boundary script: reads ticket JSON on stdin, validates it against `Ticket`,
then calls the `task` CLI. A ticket is a one-line title plus five bullet-list
sections, stored as one annotation on the task. Nothing is created unless the
whole ticket is valid and every dependency exists.

Usage:
    tw-new.py < ticket.json     create the task, print its UUID
    tw-new.py --schema          print the ticket JSON Schema
"""

import json
import subprocess
import sys
from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
)

Bullet = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=3, max_length=200, pattern=r"^[^\n]+$"
    ),
]
ProjectName = Annotated[
    str, StringConstraints(pattern=r"^[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)*$")
]
TagName = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9_-]+$")]

# Every call: never prompt for confirmation.
TASK = ("task", "rc.confirmation=off")


class Risk(BaseModel):
    """Something that could break, and how it would be noticed."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    risk: Bullet
    detection: Bullet


class Ticket(BaseModel):
    """A task title plus the reasoning sections that every ticket carries."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    title: Bullet
    project: ProjectName
    depends: list[UUID] = []
    tags: list[TagName] = []
    problem: list[Bullet] = Field(min_length=1)
    decision: list[Bullet] = Field(min_length=1)
    artifacts: list[Bullet] = Field(min_length=1)
    risks: list[Risk] = Field(min_length=1)
    done_when: list[Bullet] = Field(min_length=1)


def render_body(ticket: Ticket) -> str:
    """Return the markdown annotation for a ticket, sections in fixed order."""
    lines = ["## Problem", *(f"- {b}" for b in ticket.problem)]
    lines += ["", "## Decision", *(f"- {b}" for b in ticket.decision)]
    lines += ["", "## Artifacts", *(f"- {b}" for b in ticket.artifacts)]
    lines += ["", "## Risks"]
    for risk in ticket.risks:
        lines += [f"- {risk.risk}", f"  - Detection: {risk.detection}"]
    lines += ["", "## Done when", *(f"- [ ] {b}" for b in ticket.done_when)]
    return "\n".join(lines)


def add_arguments(ticket: Ticket) -> list[str]:
    """Return the `task add` arguments for a ticket.

    The title goes after `--`, so words in it such as `due:` or `project:` stay
    plain text and are not read as task attributes.
    """
    arguments = ["add", f"project:{ticket.project}"]
    arguments += [f"+{tag}" for tag in ticket.tags]
    if ticket.depends:
        arguments.append("depends:" + ",".join(str(u) for u in ticket.depends))
    return [*arguments, "--", ticket.title]


def format_errors(error: ValidationError) -> str:
    """Return one line per failed rule: the field path, then the reason."""
    return "\n".join(
        f"{'.'.join(str(part) for part in e['loc']) or '(ticket)'}: {e['msg']}"
        for e in error.errors()
    )


def run_task(arguments: Sequence[str], *, verbose: str = "nothing") -> str:
    """Run the `task` CLI and return its stdout.

    Raises subprocess.CalledProcessError when `task` exits non-zero.
    """
    command = [*TASK, f"rc.verbose={verbose}", *arguments]
    result = subprocess.run(
        command, capture_output=True, text=True, check=True, stdin=subprocess.DEVNULL
    )
    return result.stdout


def missing_dependencies(uuids: Sequence[UUID]) -> list[UUID]:
    """Return the UUIDs that match no task, or only a deleted one.

    Taskwarrior stores a dependency on a UUID that does not exist without an
    error, and the task is then never shown as blocked. This check prevents it.
    """
    missing = []
    for uuid in uuids:
        found = json.loads(run_task([f"uuid:{uuid}", "export"]))
        if not found or found[0]["status"] == "deleted":
            missing.append(uuid)
    return missing


def create_task(ticket: Ticket) -> str:
    """Create the task and its body annotation; return the new UUID.

    When the annotation fails, the new task is deleted again, so a failure never
    leaves a task without its ticket body.
    """
    output = run_task(add_arguments(ticket), verbose="new-uuid")
    uuid = output.strip().removeprefix("Created task ").removesuffix(".")
    try:
        run_task([uuid, "annotate", "--", render_body(ticket)])
    except subprocess.CalledProcessError:
        run_task([uuid, "delete"])
        raise
    return uuid


def main(argv: Sequence[str]) -> int:
    """Validate stdin as a ticket and create it; return the exit code."""
    if list(argv) == ["--schema"]:
        print(json.dumps(Ticket.model_json_schema(), indent=2))
        return 0
    try:
        ticket = Ticket.model_validate_json(sys.stdin.read())
    except ValidationError as error:
        print(format_errors(error), file=sys.stderr)
        return 1
    missing = missing_dependencies(ticket.depends)
    if missing:
        for uuid in missing:
            print(f"depends: no open or completed task {uuid}", file=sys.stderr)
        return 1
    try:
        print(create_task(ticket))
    except subprocess.CalledProcessError as error:
        print(f"task failed: {error.stderr.strip()}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
