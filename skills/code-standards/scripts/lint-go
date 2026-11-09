#!/bin/sh
# Run gofmt and go vet, plus golangci-lint when it is on PATH.
# Run from the module root.
set -eu

command -v gofmt >/dev/null 2>&1 || {
    echo "gofmt not found; install Go" >&2
    exit 1
}

unformatted="$(gofmt -l .)"
if [ -n "$unformatted" ]; then
    echo "unformatted files:" >&2
    echo "$unformatted" >&2
    exit 1
fi

go vet ./...

if command -v golangci-lint >/dev/null 2>&1; then
    golangci-lint run
else
    echo "golangci-lint not on PATH; skipped" >&2
fi
