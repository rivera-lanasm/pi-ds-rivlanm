# Java: standards and tools

The general standards in SKILL.md apply. This file maps them to Java.

## Functional first in Java

- Default to static methods over instance state. A class earns instances when
  it carries a resource with a lifecycle (a connection pool, a client) or an
  invariant several operations share.
- Records are the data carriers: `record Point(int x, int y) {}` gives an
  immutable value with a shape and no behavior. Use them wherever a mutable
  bean with getters would have gone.
- Sealed classes make illegal states unrepresentable: a sealed interface with
  permitted subtypes is the discriminated union of Java. Prefer it over one
  class with nullable fields and a comment about valid combinations.
- Streams are the pipeline: `map`, `filter`, `reduce` over mutable loops when
  the transform is the point. No side effects inside a stream operation.
- Composition over inheritance. Deep hierarchies move behavior away from the
  call site; pass a `Function` or a small interface instead.
- `Optional` is a return type, never a field or a parameter.

## Javadoc

Every module (`module-info.java`), package (`package-info.java`), and public
type and method carries Javadoc. State what the caller cannot see from the
signature: units, ranges, nullability, thrown conditions, thread safety. Never
restate the signature — `/** Gets the user. */` on `getUser()` costs a line
and says nothing.

## Tools

Java linting is build-tool bound; there is no universal runner script. Wire
the checks into Maven or Gradle and pin every version.

| Tool | Job |
|---|---|
| Spotless (`google-java-format`) | formatting, import order |
| Checkstyle | naming, Javadoc presence, complexity |
| Error Prone | bug patterns the compiler accepts |
| NullAway (Error Prone plugin) | null safety at the edges |

**Commands:**

```bash
./mvnw spotless:check checkstyle:check     # Maven
./gradlew spotlessCheck check              # Gradle
```

Fix warnings; do not silence them. A `@SuppressWarnings` carries the check
name and a reason on the same declaration.

## Resources

- Google Java Style Guide:
  https://google.github.io/styleguide/javaguide.html — the base style.
  Checkstyle ships it as `google_checks.xml`.
- Error Prone bug patterns: https://errorprone.info/bugpatterns — the
  catalog of checks that Error Prone adds to the compiler.
