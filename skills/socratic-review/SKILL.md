---
name: socratic-review
description: Review or draft a technical document with the maintainer through Socratic questioning — one question at a time, verify understanding, surface gaps, record outcomes. Use when a plan, proposal, or paper needs collaborative review or section-by-section drafting against source material, or when the maintainer asks to work through a document together.
---

# Socratic review

Work through a technical document with the maintainer, one question at a
time. Applies to reviewing an existing document and to drafting one
section by section against source material.
Inspired by the socratic-tutor skill in jane street's agent_skills (MIT).

Two goals, pursued together:

1. The maintainer understands every idea the document relies on.
2. The document has no gaps: unstated assumptions, ambiguous steps,
   untestable claims, missing alternatives.

## Before starting

Agree three things with the maintainer — or take them from the invoking
instruction:

- **Scope.** The whole document, or one section. When drafting, name the
  section being written.
- **Source material.** What the document must stay consistent with:
  evidence documents, data, an existing draft. Read the source material
  for the current scope before asking anything; when reviewing an
  existing document, read the document too.
- **Outcome record.** Where decisions and gaps land: appended to the
  document, a separate notes file, task annotations.

Collect the points to probe from the scope and source material: each
claim, each decision, each assumption, each rejected alternative.

Tell the maintainer how the review runs: one question at a time, no
answer handed over, gaps fixed in the document.

## Section walkthrough

- Walk the sections in the agreed order.
- For each section, let the maintainer open — with their own question
  about it, or when drafting, with what they want the section to say.
  Do not open a section with your question.
- When their opening is settled, probe the section's ideas with the
  review loop until each is confirmed or written. Then move to the next
  section.

## Review loop (repeat per discussion point)

- Ask ONE question at a time. End the message immediately after the
  question and wait for the answer; do not add hints, example answers,
  or teaching content after it.
- Prefer questions that make the maintainer: state what the source
  material shows, explain why a decision was made, find the flaw in a
  plausible-but-wrong claim, apply an idea to a new case, or connect two
  ideas in the document.
- When the maintainer is wrong, do not give the answer. Ask a narrower
  question that exposes the contradiction in their reasoning. Only
  explain directly after 2-3 failed attempts, and then immediately
  re-test the same idea from a different angle.
- When the maintainer is right, occasionally play devil's advocate
  ("are you sure? what about X?") — correct answers should hold under
  pressure.
- Give short explanations (a few sentences) only for genuinely new
  material the maintainer could not derive from the source material.
  Then return to questioning.

## Gap finding

Each answer, or failure to answer, tells you something. Diagnose which
of these happened:

- The maintainer understood and can defend the point. Mark the point
  confirmed and move on.
- The maintainer could not reason from the document or the source
  material. Either the idea needs a narrower question — loop again —
  or the document failed to explain it. Name the latter as a gap.

Probe the document itself, not only the maintainer:

- A claim with no checkable source.
- A decision with no rejected alternative.
- An idea used but not explained anywhere in the document.

Keep a gap list in the conversation as you go: the section, what it
fails to explain or decide, and the smallest fix.

## Check the source, not the summary

Where the source material is checkable — an evidence document, a file,
a command — consult it directly and compare with what the maintainer
claims it shows. Do not accept the maintainer's description of a source
in place of the source.

## Ending the review

End with three things:

- The points probed and how the maintainer showed understanding.
- The gap list, if any.
- What changed in the document, if anything.

Write the outcomes — each decision, its reasoning, and what it rules
out — to the outcome record agreed at the start. Follow-up discussions
land there too.
