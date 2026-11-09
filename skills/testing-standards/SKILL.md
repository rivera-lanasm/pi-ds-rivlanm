---
name: testing-standards
description: |
  Decide whether a test earns a permanent place in the suite, then write it.
  Use when you add, review, refactor, or delete tests; when you set up a test
  suite; when coverage is the goal; or when the user says "unit test",
  "integration test", "regression test", "test coverage", "flaky", "brittle",
  "mock", "fixture", "pytest", or "vitest". One gate controls admission: a test
  exists to catch a named failure that a real caller notices. Every test module
  carries a docstring that states which behaviors justify its tests.
---

# Testing Standards

A test suite is a liability that pays for itself. Each test costs runtime, review
attention, and one more thing to update when the code changes. A test earns its
place when it catches a failure that a real caller notices. A test that cannot
name that failure is deleted, not fixed.

Most test suites fail from the other direction. They grow until nobody trusts
them, then nobody reads them, then a real failure hides in the noise. Write
fewer tests. Make each one carry a fact.

## The Admission Gate

Before you write a test, answer this question in one sentence:

> **What does a user of this code lose when this behavior breaks?**

If you cannot answer it, do not write the test.

Three answers pass the gate:

| Answer | Tier |
|---|---|
| A rule the code decides — a branch, a boundary, a transform, an error path | **Unit** |
| A contract between two parts — a schema, a protocol, a query, a wire format | **Integration** |
| A specific bug that reached a user one time | **Regression** |

Every other answer fails. "It increases coverage" fails. "The function is
untested" fails. "It is a public method" fails.

## The Three Tiers

### Unit tests — the rules the code decides

A unit test covers a decision the code makes on its own. Good targets:

- Branch and boundary conditions. Empty input, one item, many items, the limit,
  one past the limit.
- Transforms with a known correct output. Parsers, formatters, calculations,
  scales, reducers.
- Error paths. The code must reject bad input in a named way.
- Invariants. The output preserves an ordering, a total, or a unit.

Test the behavior through the public entry point. Do not test private helpers
directly. When a private helper needs its own test, it wants to be its own
module with its own public function.

### Integration tests — the contracts between parts

An integration test covers a seam where two parts agree on a format. The parts
run for real: a real database, a real HTTP call to a local server, a real file
on disk. A mock at the seam under test defeats the test.

Good targets: a query against a real schema, a request and response against a
real route, a migration against a real database, a build that produces real
output files.

Integration tests are slower and fewer. One test per seam beats twenty tests
per seam. When you want more cases at a seam, move the case into a unit test of
the logic behind it.

### Regression tests — one bug, one test, forever

A regression test is written when a bug reaches a user, and never before. It
reproduces the bug and fails against the old code.

Every regression test names its bug in the test docstring: the symptom, the
cause, and the issue or commit. A regression test without that provenance
becomes unexplainable within a year, and then it becomes undeletable.

```python
def test_empty_series_renders_axis() -> None:
    """Regression: issue #142.

    An empty series made the y-axis domain [Infinity, -Infinity], and the chart
    rendered with no axis at all. The scale now falls back to [0, 1].
    """
```

## Reject These

Delete these on sight. Do not repair them.

**Self-referential** — the test restates the implementation. It fails when the
code changes and passes when the code is wrong in the same way.

```python
# Reject: this asserts the source code, not the behavior.
def test_discount() -> None:
    assert discount(100) == 100 * 0.9
```

Write the expected value as a literal a human agreed to: `assert discount(100) == 90`.

**Mock-dominated** — the test asserts that mocks were called. It passes when the
real system is broken.

```python
# Reject: this tests the mock library.
mock_repo.save.assert_called_once_with(user)
```

Assert the outcome instead. After the call, the user is in the store.

**Trivial** — the test covers a line with no decision in it. Getters, setters,
pass-through wrappers, dataclass constructors, re-exports, `__init__`. The type
checker already covers these.

**Brittle** — the test fails for reasons unrelated to the behavior. The usual
causes:

- Asserting on whole objects when one field carries the meaning.
- Asserting on log text, error message wording, or key order.
- Depending on the current time, the current timezone, the machine, or the
  network. Inject the clock. Freeze it.
- Depending on test execution order or on state a previous test left behind.
- Asserting on rendered markup or CSS class names when the behavior is what the
  user sees. Query by role and text.

**Bloat** — many tests that share one failure cause. Twenty parametrized cases
through the same branch catch the same bug twenty times. Keep the boundary
cases. Delete the middle.

**Snapshot tests with no reader** — a snapshot nobody reads is a record that the
code did what it did. Use a snapshot only when a human reviews the diff and can
say the new output is wrong.

## The Required Module Docstring

Every test module opens with a docstring that states which behaviors in the code
under test justify persistent tests, and which are deliberately untested. This
is the durable part. It tells the next reader why the file exists and stops the
file from growing by accretion.

The docstring answers four things:

1. **Subject** — what code this module covers.
2. **Tier** — unit, integration, or regression. Say why this tier fits.
3. **Justifies a test** — the specific behaviors that earn coverage, and the
   failure each one catches.
4. **Deliberately untested** — what is out of scope here, and where it is
   covered instead, or why it needs no cover.

Python:

```python
"""Unit tests for the retry policy in `client.retry`.

Tier: unit. The policy is pure — it maps an attempt count and an error to a
delay — so its rules are testable without a network.

Justifies a test:
  - The backoff schedule. A wrong exponent silently turns a 3-second retry
    budget into a 300-second one, and callers time out.
  - The retryable/fatal split. Retrying a 400 wastes the budget; not retrying
    a 503 drops a request the server invited us to resend.
  - The attempt ceiling. Off-by-one here means one extra call against a
    rate-limited endpoint.

Deliberately untested:
  - Jitter values. Random by design; the test asserts the range, not the draw.
  - Actual sleeping. The clock is injected. Real timing is covered once in
    tests/integration/test_client_timing.py.
  - Logging output. Log text is not a contract.
"""
```

TypeScript:

```ts
/**
 * Unit tests for the linear scale wrapper in `src/lib/scale.ts`.
 *
 * Tier: unit. The wrapper is a pure mapping from data domain to pixel range.
 *
 * Justifies a test:
 *  - Domain inversion (max < min). Produces a mirrored chart, which reads as
 *    real data rather than as a bug.
 *  - The empty and single-point domains. Both collapse the range to zero width
 *    and render an invisible axis.
 *  - Clamping at the range edges. An unclamped point draws outside the SVG
 *    viewport and is silently invisible.
 *
 * Deliberately untested:
 *  - d3-scale itself. It is a dependency with its own suite.
 *  - Tick label formatting. Covered by the axis component tests.
 */
```

When you add a test to an existing module, add its justification to the
docstring in the same change. When the justification duplicates one already
listed, you are writing bloat — stop.

## Writing the Test

- **The name is the claim.** `test_expired_token_is_rejected`, not `test_auth_2`.
  A reader who sees only the failing test name knows what broke.
- **One behavior per test.** A test with three unrelated assertions reports one
  failure for three causes.
- **Assert the outcome, not the path.** What the caller observes, not which
  functions ran.
- **Build inputs with an explicit factory.** A helper that takes the one field
  the test cares about and fills the rest with defaults. Shared mutable fixtures
  create order dependence.
- **No conditionals or loops in a test body.** A test with an `if` has an
  untested branch of its own.
- **Fail first.** Run the test against the unfixed code and watch it fail. A
  test that has never failed proves nothing.

## Deleting Tests

Deleting a test is normal work, not damage. Delete when:

- The behavior it covers is gone.
- Its module docstring cannot justify it.
- It fails intermittently and the cause is in the test.
- Another test in the same file fails for the same reason.

State the deletion and the reason in the commit message. Never delete a test to
make a build pass. When a test fails and the code is right, the test is wrong —
say which, and why.

## Coverage

Coverage finds untested code. It does not grade a suite. A module at 100% built
from trivial tests is worse than one at 60% built from real ones, because the
number claims a safety that is not there.

Use coverage as a question, not a target: read the uncovered lines, and for each
one apply the admission gate. Most uncovered lines are correctly uncovered. Do
not set a coverage threshold that a build enforces — it converts the gate into a
quota and manufactures exactly the tests this document rejects.
