---
name: d2-diagrams
description: Author D2 diagrams that convey one specific idea without overwhelming the reader. Use when a plan, proposal, or documentation needs a diagram and names D2.
---

Draw diagrams that convey one specific idea. If a diagram needs a caption to
explain what it shows, it shows too much.

## Before drawing

- Name the one idea the reader must see.
- Keep a diagram to five shapes or fewer.
- A diagram that exceeds five shapes signals that the idea needs splitting.
  Break it into diagrams that each focus on one aspect: one high-level
diagram, still grounded in real method calls and names, then further
diagrams that zoom in on nodes from the high-level one. A reader who
  wants detail follows the zoom-in; a reader who wants the point reads the
  high-level diagram only.

## Choosing the form

Match the content to D2's shape kinds. Use a special form when the content
is that thing; otherwise use plain boxes and arrows.

- Ordered handoffs or interactions over time: `shape: sequence_diagram`.
  Order follows definition order.
  https://d2lang.com/tour/sequence-diagrams/
- A data record or type: `shape: sql_table` for table rows and
  constraints; `shape: class` for fields and methods.
  https://d2lang.com/tour/sql-tables/, https://d2lang.com/tour/uml-classes/
- A matrix or fixed arrangement: `grid-rows` or `grid-columns` on the
  container; cells fill evenly. https://d2lang.com/tour/grid-diagrams/
- A literal snippet or equation inside the diagram: `shape: text` or
  `shape: code` with a language; `latex` for math notation.
  https://d2lang.com/tour/text/
- Grouping that reads as one system: containers, at most two levels.
- A shape that auto-sizes badly, or nodes that must line up: set `width`
  or `height` on it. https://d2lang.com/tour/dimensions/
- Everything else: boxes and arrows.

## Conventions

- Use concrete labels from the real system: file paths, port numbers, route
  names, resource names. Never "Component A" or "Service B".
- Keep node labels minimal: a name, a path, or a role — enough to identify
  the node, nothing more. Detail does not belong in the shape.
- Follow each diagram with a short bullet list: one bullet per node, what
  it represents, with the full path and context when useful. The list
  carries the detail; the shapes carry the structure.
- Left-to-right for flows and pipelines. Top-down for hierarchy.
- Use containers to group related shapes. Go at most two levels deep.
- Label connections with the real protocol, port, or trigger: `HTTPS`,
  `port 80`, `on merge`.

Syntax reference:

```d2
visitor -> vpc.alb: HTTPS
vpc: VPC 10.0.0.0/16 {
  alb: ALB
  node: EC2 k3s node
  alb -> node: HTTP port 80
}
```

## Styling

- One theme for all diagrams in a document. Pick it with `d2 themes`
  and name the choice in the document.
- No per-shape color unless it marks the single point the diagram makes.
- No icons and no sketch mode unless the reader needs them.
- Share one style across many shapes with classes, not repeated
  attributes. See https://d2lang.com/tour/classes/.

## Storage

- Store a document's diagrams in a subfolder named after the document,
  without its `.md` suffix: for `deploy.md`, they live in `diagrams/deploy/`
  beside the document. Keep the `.d2` source and the rendered `.svg` together
  there.
- Reference the SVG from the document with a relative path, such as
  `![Build pipeline](diagrams/deploy/build-pipeline.svg)`.
- Name diagram files after the idea they show, not after a task.
- One document's diagrams regenerate or delete together. Keep them out of
  folders other documents own.

## Render

```sh
d2 --pad 20 path/to/diagram.d2 path/to/diagram.svg
```

- Render at the default scale. The HTML preview displays an SVG at its
  intrinsic size, so the rendered size is the display size. Do not scale
  up.
- `--pad 20` trims the default 100-pixel margin, which dominates a small
  diagram.
- After rendering, check the SVG's width and height. When the width
  exceeds about three times the height, a width-constrained preview
  shrinks the text below legibility. Shorten the labels, lay the chain
  top-down, or split the diagram, and render again.
- Confirm the render command succeeds before handing back the work.
- Place each diagram next to the text it supports.
