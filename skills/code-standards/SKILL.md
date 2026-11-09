---
name: code-standards
description: |
  Apply these standards when you write, refactor, or review code in any
  language. Covers what a linter cannot check: functional design over class
  hierarchies, separation of concerns, docstring content, type coverage at the
  boundaries, and naming. Language-specific tools and guidance for Python,
  Go, Java, and TypeScript live under references/, with lint runners under
  scripts/. Use when starting a new module or package, restructuring existing
  code, reviewing a diff, setting up linting or formatting, or when the user
  says "refactor", "clean up", "code review", "ruff", "lint", "type
  hints", or "docstring".
---

# Code Standards

## Division of Labor

A linter enforces mechanical rules and never gets tired. Spend no attention on
what it already covers.

| Deterministic — the tool decides | Judgment — you decide |
|---|---|
| Line length, quotes, import order, trailing commas | Where a boundary belongs |
| Unused variables and imports, shadowed names | Whether a class earns its state |
| Mutable default arguments, bare `except` | What a docstring must say |
| Missing type annotations (as a rule set) | Whether a type describes the real domain |
| Naming *convention* (snake_case, PascalCase) | Whether a name is *true* |

Run the tool first. Read what remains.

## Functional First

Default to functions over classes. A function has one entry point, one visible
input set, and one output. A class has as many entry points as methods, and each
one can read and write state that no signature mentions.

**Write pure functions.** Same input, same output, no observable effect. A pure
function is testable without setup, readable without context, and reusable
without a lifecycle.

**Move state to the edges.** Compute with data, not with objects that hold data
and act on it at once. Take values in, return new values out.

```python
# Avoid: state and behavior fused, mutation hidden behind method calls.
class ReportBuilder:
    def __init__(self, rows): self.rows = rows
    def filter_active(self): self.rows = [r for r in self.rows if r.active]
    def build(self): return "\n".join(...)

# Prefer: a pipeline of transforms, each usable on its own.
def keep_active(rows: Sequence[Row]) -> list[Row]: ...
def render_report(rows: Sequence[Row]) -> str: ...
```

**Prefer immutability.** Return a new value; do not mutate an argument. Use
frozen dataclasses, tuples, and `Sequence`/`Mapping` parameter types. When a
function mutates its argument, its name says so (`append_`, `update_`) and it
returns `None`.

**Prefer composition to inheritance.** Pass a function in. Deep hierarchies move
behavior somewhere the reader cannot see from the call site.

**Use small data carriers.** A frozen dataclass, a `TypedDict`, a Pydantic model
at a boundary, a plain record type. Data with a shape and no behavior.

### When a class is the right answer

Use a class when it carries something a function cannot:

- **A resource with a lifecycle.** A connection pool, a file handle, a client
  that must open and close. Give it a context manager.
- **A protocol or interface.** `typing.Protocol` for structural typing, or an
  ABC when the language demands one.
- **Real invariant-bearing state** that many operations share, where passing it
  as a parameter every time is worse.
- **A framework requirement.** A Pydantic model, a Django model, a pytest
  fixture class. Follow the framework.

Do not use a class as a namespace for functions that never touch `self`. That is
a module.

## Types

Every function signature carries types: parameters and return. In Python this is
a lint rule (`ANN`) and a type checker's job — turn both on and stop thinking
about it.

What is left to judgment:

- **Type the domain, not the container.** `dict[str, Any]` states nothing.
  Define the record type. `Any` is a request for a runtime bug.
- **Types narrow at the boundary.** Untrusted input arrives as `str` or `bytes`,
  and is parsed into a validated type once, at the edge. Inside the core, the
  data is already valid. Pydantic at the Python edge; a parsed and validated
  type at the TypeScript edge.
- **Accept wide, return narrow.** Take `Sequence[T]` or `Iterable[T]`; return
  `list[T]`. Take `Mapping`; return `dict`.
- **Make illegal states unrepresentable.** A union of two shapes beats one shape
  with four optional fields and a comment about which combinations are real.
- **A `# type: ignore` carries a reason** on the same line.

## Docstrings

Every module and every public function has a docstring. A docstring states what
the code is for and what the reader cannot see from the signature. It never
restates the signature.

**Module docstring** — one line naming the module's single responsibility, then
what belongs here and what does not. When the module has a boundary role
(reads the network, touches the database, writes files), say so.

```python
"""Parse and validate incoming webhook payloads.

Boundary module: every value here arrives untrusted and leaves as a validated
`WebhookEvent`. No network calls, no database access, no logging side effects —
callers decide what to do with the parsed event.
"""
```

**Function docstring** — what it does, in the imperative. Then only the parts a
reader cannot infer: units, ranges, and formats; what it raises and when; side
effects; performance characteristics that affect a caller; the reason behind a
non-obvious choice.

```python
def backoff_delay(attempt: int, *, base_ms: int = 100) -> float:
    """Return the delay in seconds before the given retry attempt.

    `attempt` is 1-based; attempt 1 returns 0.0 and retries immediately. The
    delay doubles per attempt and is capped at 30 seconds, so a caller's total
    retry budget grows linearly after attempt 9.

    Raises ValueError when `attempt` is less than 1.
    """
```

Do not write `"""Get the user."""` above `def get_user(...)`. It costs a line
and says nothing. When a public function's docstring can only restate its name,
the name is good — write the constraints, the failure modes, or nothing.

Keep docstrings true. A docstring that contradicts the code is worse than none,
because a reader believes it. When you change behavior, change the docstring in
the same commit.

## Separation of Concerns

One module, one reason to change. Ask what would force an edit to this file. Two
unrelated answers means two modules.

**The shape to aim for:**

```
edge (I/O, parsing, validation)  →  core (pure logic)  →  edge (I/O, rendering)
```

The core does not know where the data came from or where it goes. It takes
values and returns values. This is what makes it testable without mocks — see
the `testing-standards` skill.

**Rules that follow from it:**

- Do not mix I/O with computation in one function. A function that fetches,
  computes, and writes is three functions.
- Push side effects up. A caller performs them; the callee returns a
  description of what to do.
- Dependencies point inward. The core imports nothing from the edges.
- No business rules in a route handler, a template, a migration, or a CLI parser.
  Those are transport. They call the core.
- Configuration is read once at the entry point and passed down. No module reads
  environment variables at import time.

## Naming

Names are the highest-leverage thing in a file, and no tool checks them.

- **A name states what the thing is, not how it was built.** `active_users`, not
  `filtered_list_2`.
- **One concept, one word, everywhere.** Pick `user` or `account` and never
  alternate. A synonym reads as a distinction the reader must resolve.
- **Booleans read as a claim:** `is_expired`, `has_children`, `should_retry`.
- **Functions are verbs; values are nouns.** `parse_config` returns `config`.
- **Say the unit in the name** when a number has one: `timeout_seconds`,
  `size_bytes`, `delay_ms`. Most unit bugs are naming bugs.
- **Length matches scope.** A loop index is `i`. A module-level constant spells
  itself out.
- **No abbreviations except the ones the domain already uses.** `url`, `id`, and
  `db` are fine. `usr_cfg_mgr` is not.
- **Do not encode types in names.** The type annotation does that.
- **Rename the moment a name goes stale**, in its own mechanical commit,
  separate from behavior changes.

## Language Guides

The standards above are language-independent. For the tools, setup, and
idioms of one language, read the matching reference and use the runner:

| Language | Reference | Runner |
|---|---|---|
| Python (ruff, uv) | `references/python.md` | `scripts/lint-python` |
| Go (gofmt, vet, golangci-lint) | `references/go.md` | `scripts/lint-go` |
| Java (Spotless, Checkstyle, Error Prone) | `references/java.md` | none — linting is build-tool bound |
| TypeScript / Svelte (ESLint, Biome) | `references/typescript.md` | none yet |

Pin every linter version, in every language. An unpinned linter turns a
routine dependency update into a red CI run.
