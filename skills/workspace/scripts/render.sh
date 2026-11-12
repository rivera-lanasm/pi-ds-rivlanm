#!/bin/sh
# Render a workspace markdown document to HTML, with the harness header.
#
# Usage: render <document.md> [output.html]
#
# The header (~/.pi/agent/doc-preview-header.html) styles diff blocks and
# makes images responsive. The script uses it when it exists and renders
# plain HTML when it does not. Prints the output path.
set -eu

header="${PI_AGENT_DIR:-$HOME/.pi/agent}/doc-preview-header.html"

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
    echo "usage: render <document.md> [output.html]" >&2
    exit 2
fi
input="$1"
output="${2:-${input%.md}.html}"

if [ ! -f "$input" ]; then
    echo "render: no file $input" >&2
    exit 1
fi

if [ -f "$header" ]; then
    pandoc --standalone --include-in-header="$header" -o "$output" "$input"
else
    echo "render: no header at $header; rendering without styles" >&2
    pandoc --standalone -o "$output" "$input"
fi
echo "$output"
