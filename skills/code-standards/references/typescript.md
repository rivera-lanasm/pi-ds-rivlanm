# TypeScript / Svelte: standards and tools

The general standards in SKILL.md apply. This file maps them to TypeScript
and Svelte.

| Concern | TypeScript / Svelte |
|---|---|
| Lint + format | ESLint + Prettier, or Biome |
| Types | `tsconfig` with `"strict": true`; no `any` |
| Boundary validation | Zod, or a hand-written type guard |
| Data carriers | `type` aliases and discriminated unions |
| Docstrings | TSDoc `/** */` on every module and exported symbol |
| Immutability | `readonly`, `as const`, no array mutation |

Prefer `type` to `interface` for data, plain functions to classes, and
discriminated unions to optional-field bags. `any` at a boundary is the same
bug as `dict[str, Any]` in Python.
