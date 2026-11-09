# Python: tools and setup

Ruff is the linter and formatter. It replaces flake8, isort, pyupgrade, and
black. uv runs it.

**Pin the version.** As of v0.16.0 ruff enables 413 rules by default, up from
59. An unpinned ruff turns a routine dependency update into a red CI run.

```toml
# pyproject.toml
[project.optional-dependencies]
dev = ["ruff==0.16.0"]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
# The v0.16 defaults already catch syntax errors and immediate runtime errors.
# These add the standards this document cares about.
extend-select = [
    "ANN",   # every signature is typed
    "D",     # docstrings exist and are formatted
    "I",     # import order
    "N",     # naming conventions
    "B",     # bugbear: mutable defaults, unused expressions
    "BLE",   # no bare or overly broad except
    "DTZ",   # no naive datetimes
    "RET",   # simplify returns
    "SIM",   # simplify comprehensions and conditionals
    "PTH",   # pathlib over os.path
    "C90",   # cyclomatic complexity
    "ARG",   # unused arguments
    "TID",   # no relative imports across packages
]
ignore = [
    "D203",  # conflicts with D211
    "D213",  # conflicts with D212
]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["ANN201", "D103"]  # test functions need no return type or docstring
```

**Commands:**

```bash
uv run ruff check .            # lint, pinned version
uv run ruff check . --fix      # apply safe fixes
uv run ruff format .           # format
uvx ruff@latest check .        # preview a newer ruff before you bump the pin
```

`--unsafe-fixes` changes behavior, not only style. Run it on a clean working
tree and read the whole diff.

Fix warnings; do not silence them. A `# noqa` carries the rule code and a reason:
`# noqa: BLE001 - third-party client raises bare Exception`.

**Types.** Annotations on every signature (the `ANN` rules above), checked by
mypy or pyright in strict mode. Pydantic validates untrusted input at the
boundary. Frozen dataclasses and `TypedDict` carry data.

**Runner:** `scripts/lint-python` in this skill runs the pinned check and
format pass, with `uvx` as a fallback when the project has no dev dependencies
installed.
