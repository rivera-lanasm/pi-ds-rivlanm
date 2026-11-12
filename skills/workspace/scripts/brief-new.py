#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pydantic>=2.7,<3"]
# ///
"""Write the brief for one ws- agent from validated input.

A brief is the task text that the main session gives to a subagent when it
starts the subagent. Boundary script: reads brief JSON on stdin, validates it
against the model of the agent, checks each value against the workspace on
disk and against Taskwarrior, then prints the brief text. Nothing is printed
to stdout unless the whole brief is valid. The script changes no file and no
task.

For ws-architect and ws-coder, the title and the reasoning come from the
ticket in Taskwarrior. The input gives only the ticket UUID.

Usage:
    brief-new.py <agent> < brief.json   print the brief text
    brief-new.py --schema <agent>       print the JSON Schema of the input

<agent> is ws-researcher, ws-architect, or ws-coder.
"""

import json
import re
import subprocess
import sys
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
)

Line = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=3, max_length=300, pattern=r"^[^\n]+$"
    ),
]
RepoName = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9._-]+$")]
# <topic>-<number>.md. A fork appends a sub-number: auth-1.1.md forks auth-1.md.
ResearchName = Annotated[
    str, StringConstraints(pattern=r"^[a-z0-9]+(-[a-z0-9]+){0,4}-\d+(\.\d+)*\.md$")
]

# Every call: never prompt for confirmation, print only the data.
TASK = ("task", "rc.confirmation=off", "rc.verbose=nothing")
# A sentence end that is followed by more text.
SENTENCE_BREAK = re.compile(r"[.?!]\s+\S")
# First line of the reasoning annotation that tw-new.py writes.
REASONING_START = "## Problem"


class ResearcherBrief(BaseModel):
    """The work of one ws-researcher run: one question, one new document."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    workspace: Path = Field(description="Absolute path of the workspace.")
    question: Line = Field(description="The research question. One sentence.")
    document: ResearchName = Field(
        description="File name of the new research document: <topic>-<number>.md. "
        "A fork of auth-1.md is auth-1.1.md."
    )
    context: list[Line] = Field(
        min_length=1,
        description="Each repository, document, or page that the research reads.",
    )
    earlier_research: list[ResearchName] = Field(
        default=[], description="File names in research/ to build on."
    )


class ArchitectBrief(BaseModel):
    """The work of one ws-architect run: the proposal document of one ticket."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    workspace: Path = Field(description="Absolute path of the workspace.")
    ticket: UUID = Field(description="UUID of the ticket that needs a design.")
    work_repos: list[RepoName] = Field(
        min_length=1, description="Names under repos/ that the design changes."
    )
    research: list[ResearchName] = Field(
        default=[], description="File names in research/ that the design uses."
    )


class ProposalWork(BaseModel):
    """The coder implements the approved proposal document of the ticket."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: Literal["proposal"]


class InstructionWork(BaseModel):
    """The coder implements a direct instruction of the user."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: Literal["instruction"]
    lines: list[Line] = Field(min_length=1)


class CoderBrief(BaseModel):
    """The work of one ws-coder run: the implementation of one ticket."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    workspace: Path = Field(description="Absolute path of the workspace.")
    ticket: UUID = Field(description="UUID of the ticket to implement.")
    work: ProposalWork | InstructionWork = Field(
        discriminator="kind",
        description="The source of the work: the proposal document of the "
        "ticket, or instruction lines from the user.",
    )
    repos: list[RepoName] = Field(
        min_length=1, description="Names under repos/ that the agent can change."
    )
    guidance: Path | None = Field(
        default=None, description="Absolute path of a guidance document, or null."
    )


Brief = ResearcherBrief | ArchitectBrief | CoderBrief

MODELS: dict[str, type[Brief]] = {
    "ws-researcher": ResearcherBrief,
    "ws-architect": ArchitectBrief,
    "ws-coder": CoderBrief,
}


@dataclass(frozen=True)
class Ticket:
    """The parts of a Taskwarrior ticket that a brief quotes."""

    uuid: UUID
    title: str
    reasoning: str

    @property
    def ticket_id(self) -> str:
        """The first 8 characters of the UUID. It names the ticket documents."""
        return str(self.uuid)[:8]


# --- Checks against the disk. Each returns one line per problem. ---


def check_workspace(root: Path) -> list[str]:
    """Check that root is an absolute path of a workspace with its AGENTS.md."""
    if not root.is_absolute():
        return [f"workspace: {root} is not an absolute path"]
    if not root.is_dir():
        return [f"workspace: no directory at {root}"]
    if not (root / "AGENTS.md").is_file():
        return [f"workspace: no AGENTS.md in {root}; the agent reads it first"]
    return []


def declared_work_repos(root: Path) -> set[str] | None:
    """Return the work repos that workspace.toml declares, or None without the file.

    Raises ValueError when the file is not valid TOML.
    """
    path = root / "workspace.toml"
    if not path.is_file():
        return None
    try:
        data = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"workspace.toml: {error}") from None
    repos = data.get("repos", {})
    work = repos.get("work", []) if isinstance(repos, dict) else []
    return {name for name in work if isinstance(name, str)}


def check_repos(root: Path, names: Sequence[str], field: str) -> list[str]:
    """Check that each name is a directory under repos/ and a declared work repo."""
    try:
        declared = declared_work_repos(root)
    except ValueError as error:
        return [str(error)]
    problems = []
    for name in names:
        if not (root / "repos" / name).is_dir():
            problems.append(f"{field}: no directory at repos/{name}")
        elif declared is not None and name not in declared:
            problems.append(
                f"{field}: workspace.toml does not declare {name} as a work repo"
            )
    return problems


def check_research_exists(root: Path, names: Sequence[str], field: str) -> list[str]:
    """Check that each named research document exists."""
    return [
        f"{field}: no document at research/{name}"
        for name in names
        if not (root / "research" / name).is_file()
    ]


def fork_parent(name: str) -> str | None:
    """Return the document that a fork derives from, or None for a first-level name.

    "auth-1.1.md" forks "auth-1.md"; "auth-1.2.3.md" forks "auth-1.2.md".
    """
    stem = name.removesuffix(".md")
    topic, _, number = stem.rpartition("-")
    if "." not in number:
        return None
    return f"{topic}-{number.rpartition('.')[0]}.md"


def check_researcher(brief: ResearcherBrief) -> list[str]:
    """Check the values of a researcher brief against the workspace."""
    root = brief.workspace
    problems = check_workspace(root)
    if problems:
        return problems
    if SENTENCE_BREAK.search(brief.question):
        problems.append("question: more than one sentence; narrow the question")
    if (root / "research" / brief.document).exists():
        problems.append(f"document: research/{brief.document} already exists")
    parent = fork_parent(brief.document)
    if parent is not None and not (root / "research" / parent).is_file():
        problems.append(f"document: a fork needs its parent research/{parent}")
    problems += check_research_exists(root, brief.earlier_research, "earlier_research")
    return problems


def check_architect(brief: ArchitectBrief) -> list[str]:
    """Check the values of an architect brief against the workspace."""
    root = brief.workspace
    problems = check_workspace(root)
    if problems:
        return problems
    problems += check_repos(root, brief.work_repos, "work_repos")
    problems += check_research_exists(root, brief.research, "research")
    return problems


def check_coder(brief: CoderBrief) -> list[str]:
    """Check the values of a coder brief against the workspace."""
    root = brief.workspace
    problems = check_workspace(root)
    if problems:
        return problems
    problems += check_repos(root, brief.repos, "repos")
    if isinstance(brief.work, ProposalWork):
        proposal = root / "proposals" / f"{str(brief.ticket)[:8]}.md"
        if not proposal.is_file():
            problems.append(f"work: no proposal document at {proposal}")
    if brief.guidance is not None:
        if not brief.guidance.is_absolute():
            problems.append(f"guidance: {brief.guidance} is not an absolute path")
        elif not brief.guidance.is_file():
            problems.append(f"guidance: no file at {brief.guidance}")
    return problems


# --- Taskwarrior. ---


def read_ticket(uuid: UUID) -> Ticket:
    """Read one pending ticket from Taskwarrior.

    Raises ValueError when no task has the UUID, when the task is not pending,
    or when the task has no reasoning annotation from tw-new.py. Raises
    subprocess.CalledProcessError when `task` exits non-zero.
    """
    result = subprocess.run(
        [*TASK, f"uuid:{uuid}", "export"],
        capture_output=True,
        text=True,
        check=True,
        stdin=subprocess.DEVNULL,
    )
    found = json.loads(result.stdout)
    if not found:
        raise ValueError(f"ticket: no task {uuid}")
    task = found[0]
    if task["status"] != "pending":
        raise ValueError(f"ticket: task {uuid} is {task['status']}, not pending")
    bodies = [
        note["description"]
        for note in task.get("annotations", [])
        if note["description"].startswith(REASONING_START)
    ]
    if not bodies:
        raise ValueError(f"ticket: task {uuid} has no reasoning from tw-new.py")
    return Ticket(uuid=uuid, title=task["description"], reasoning=bodies[0])


# --- Rendering. Pure: values in, brief text out. ---


def bullets(items: Sequence[object]) -> list[str]:
    """Return one bullet line per item, or one "none" bullet for no items."""
    return [f"- {item}" for item in items] or ["- none"]


def ticket_lines(ticket: Ticket) -> list[str]:
    """Return the lines that identify a ticket."""
    return [f"Ticket: {ticket.ticket_id} ({ticket.uuid})", f"Title: {ticket.title}"]


def render_researcher(brief: ResearcherBrief) -> str:
    """Return the brief text for ws-researcher."""
    research = brief.workspace / "research"
    lines = [
        f"Workspace: {brief.workspace}",
        f"Question: {brief.question}",
        f"Document: {research / brief.document}",
        "Context set:",
        *bullets(brief.context),
        "Earlier research:",
        *bullets([research / name for name in brief.earlier_research]),
    ]
    return "\n".join(lines)


def render_architect(brief: ArchitectBrief, ticket: Ticket) -> str:
    """Return the brief text for ws-architect."""
    root = brief.workspace
    lines = [
        f"Workspace: {root}",
        *ticket_lines(ticket),
        f"Document: {root / 'proposals' / (ticket.ticket_id + '.md')}",
        "Work repos:",
        *bullets([root / "repos" / name for name in brief.work_repos]),
        "Research:",
        *bullets([root / "research" / name for name in brief.research]),
        "",
        "Reasoning of the ticket:",
        ticket.reasoning,
    ]
    return "\n".join(lines)


def render_coder(brief: CoderBrief, ticket: Ticket) -> str:
    """Return the brief text for ws-coder."""
    root = brief.workspace
    if isinstance(brief.work, ProposalWork):
        proposal = root / "proposals" / (ticket.ticket_id + ".md")
        work = [f"Source of the work: the proposal document {proposal}"]
    else:
        work = ["Source of the work: the instruction of the user:"]
        work += bullets(brief.work.lines)
    lines = [
        f"Workspace: {root}",
        *ticket_lines(ticket),
        *work,
        "Repos in scope:",
        *bullets([root / "repos" / name for name in brief.repos]),
        f"Guidance document: {brief.guidance or 'none'}",
        "",
        "Reasoning of the ticket:",
        ticket.reasoning,
    ]
    return "\n".join(lines)


def build(brief: Brief) -> tuple[list[str], str]:
    """Check one brief and render it; return the problems and the brief text.

    The text is empty when there are problems. Reads the disk, and reads
    Taskwarrior for a brief that names a ticket.
    """
    if isinstance(brief, ResearcherBrief):
        problems = check_researcher(brief)
        return problems, "" if problems else render_researcher(brief)
    problems = (
        check_architect(brief)
        if isinstance(brief, ArchitectBrief)
        else check_coder(brief)
    )
    try:
        ticket = read_ticket(brief.ticket)
    except ValueError as error:
        return [*problems, str(error)], ""
    if problems:
        return problems, ""
    if isinstance(brief, ArchitectBrief):
        return [], render_architect(brief, ticket)
    return [], render_coder(brief, ticket)


def format_errors(error: ValidationError) -> str:
    """Return one line per failed rule: the field path, then the reason."""
    return "\n".join(
        f"{'.'.join(str(part) for part in e['loc']) or '(brief)'}: {e['msg']}"
        for e in error.errors()
    )


def main(argv: Sequence[str]) -> int:
    """Validate stdin as the brief of one agent and print it; return the exit code."""
    arguments = list(argv)
    want_schema = arguments[:1] == ["--schema"]
    names = arguments[1:] if want_schema else arguments
    if len(names) != 1 or names[0] not in MODELS:
        known = ", ".join(MODELS)
        print(f"usage: brief-new.py [--schema] <agent>; agents: {known}", file=sys.stderr)
        return 2
    model = MODELS[names[0]]
    if want_schema:
        print(json.dumps(model.model_json_schema(), indent=2))
        return 0
    try:
        brief = model.model_validate_json(sys.stdin.read())
    except ValidationError as error:
        print(format_errors(error), file=sys.stderr)
        return 1
    try:
        problems, text = build(brief)
    except subprocess.CalledProcessError as error:
        print(f"task failed: {error.stderr.strip()}", file=sys.stderr)
        return 1
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
