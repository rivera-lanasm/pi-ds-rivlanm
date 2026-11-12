#!/bin/sh
# Run the pinned ruff check and format pass. Falls back to uvx when the
# project has no dev dependencies installed. Run from the project root.
set -eu

command -v uv >/dev/null 2>&1 || {
    echo "uv not found; see https://docs.astral.sh/uv/" >&2
    exit 1
}

if uv run ruff --version >/dev/null 2>&1; then
    uv run ruff check .
    uv run ruff format --check .
else
    echo "ruff not in project dependencies; using unpinned uvx ruff" >&2
    uvx ruff check .
    uvx ruff format --check .
fi
