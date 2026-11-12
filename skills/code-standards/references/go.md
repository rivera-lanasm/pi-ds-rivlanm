# Go: standards and tools

The general standards in SKILL.md apply. This file maps them to Go.

## Functional first in Go

- Default to plain functions. A method earns its receiver only when the struct
  holds real state: a resource with a lifecycle (`*sql.DB`, a server, a client)
  or an invariant several operations share.
- Take values in, return new values out. When a function must mutate its
  argument (append on a slice, fill a buffer), the name says so and the caller
  passes the argument explicitly.
- Accept interfaces, return structs. Wide in, narrow out — the Go form of the
  same rule. Define interfaces at the consumer, not the producer.
- Small structs with exported fields and no methods are the data carriers.
  They are the frozen dataclass of Go.
- Compose with function values and embedding. Inheritance does not exist;
  deep embedding chains hide behavior the same way class hierarchies do.

## Errors

- Handle every error or deliberately pass it up. A bare `_` discard carries a
  comment with the reason.
- Wrap with context: `fmt.Errorf("parse config: %w", err)`. Sentinel errors
  with `errors.Is`; typed errors with `errors.As`.
- No panics in library code. Panic is for programmer error at startup.

## Doc comments

Every exported symbol has a doc comment: one complete sentence that starts
with the symbol's name, then the constraints a reader cannot see from the
signature — units, error conditions, concurrency rules. A package comment in
one file names the package's single responsibility.

```go
// BackoffDelay returns the delay before the given retry attempt.
// attempt is 1-based; attempt 1 returns 0. The delay doubles per attempt
// and is capped at 30 seconds.
func BackoffDelay(attempt int, base time.Duration) time.Duration {
```

## Tools

| Tool | Job |
|---|---|
| `gofmt` / `goimports` | formatting, import order |
| `go vet` | suspicious constructs the compiler accepts |
| `staticcheck` or `golangci-lint` | the judgment-adjacent rules: unused code, error discards, complexity |
| `errcheck` (via golangci-lint) | unchecked errors |

Pin the linter version in CI. An unpinned golangci-lint is the same trap as an
unpinned ruff.

**Commands:**

```bash
gofmt -l .                  # lists unformatted files; empty is good
go vet ./...
golangci-lint run           # when the project carries it
```

**Runner:** `scripts/lint-go.sh` in this skill runs gofmt and vet, and
golangci-lint when it is on PATH.

## Resources

- Google Go Style Guide: https://google.github.io/styleguide/go/ — decisions
  and best practices. The closest thing to a canonical Go style document.
- Effective Go: https://go.dev/doc/effective_go — the language team's own
  guidance.
- Go Code Review Comments: https://go.dev/wiki/CodeReviewComments — the
  rules that reviewers enforce on Go code.
- staticcheck checks: https://staticcheck.dev/docs/checks/ — the rule
  catalog. Read it when you decide what to enable.
