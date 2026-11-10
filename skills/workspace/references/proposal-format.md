# Proposal document format

A proposal document holds the design for one task, written before
implementation. The document has two authors. The architect writes the
design. The maintainer (the user) writes the Maintainer blocks: questions,
understanding, and the final summary.

The order matters. The maintainer writes their understanding before any
dialogue with the agent. When the agent writes the summary first, the
maintainer reads instead of thinks. The maintainer's own words are the
record of their understanding.

## Lifecycle

1. The architect subagent drafts the document. Follow the format below.
2. Render the document. Follow the render section.
3. The maintainer reads the HTML.
4. The maintainer writes their questions and their understanding in the
   Maintainer blocks. This draft comes before any dialogue with the agent.
5. Run the socratic review against the Maintainer blocks. Follow the
   socratic-review skill: one question at a time.
6. When the review finds a gap in the design, the agent fixes the architect
   text. When the review finds a gap in the understanding, the maintainer
   revises their block.
7. Render the document again after every change.
8. The review ends when each Maintainer block holds the maintainer's final
   summary. The maintainer then decides about implementation.

## Format

```markdown
# <ticket-id>: <title>

Ticket: <uuid>

## Objective

<What the task must achieve, and why.>

### Maintainer

<Questions, then understanding. Ends as the final summary of the objective.>

## Idea

<The design: approach, structure, key decisions.>

### Maintainer

<Questions, then understanding. Ends as the final summary of the idea.>

## Implementation

### Step 1: <name>

<What the step does.>

#### Maintainer

<Questions, then understanding. Ends as the final summary of the step.>

## Alternatives

<Each rejected option, and the reason.>

### Maintainer

<Questions, then understanding.>
```

## Rules

- Only the agent writes the design sections. Only the maintainer writes the
  Maintainer blocks. The agent reads the Maintainer blocks before each
  question.
- The maintainer overwrites their blocks during the review. The document
  keeps no old versions.
- The agent writes with the simple-english rules. The maintainer writes in
  their own words.

## Render

Render the document after every change:

```bash
pandoc --standalone -o proposals/<ticket-id>.html proposals/<ticket-id>.md
```

The markdown is the source. The maintainer reads the HTML.
