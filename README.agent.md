# web-gui-mcp Agent Guide

This file is optimized for coding agents and LLMs. Read it when you need to connect,
use, test, or modify `web-gui-mcp`.

## What This Server Does

`web-gui-mcp` is a local stdio MCP server that turns compact `ArtifactSpec` JSON into
safe deterministic HTML surfaces. Use it when a text-only response would be hard to
scan and the user needs a rich artifact such as a review workspace, comparison sheet,
implementation handoff, module map, report, explainer, prototype flow, or lightweight
editor.

It exposes these MCP tools:

- `search_artifact_patterns`
- `get_artifact_schema`
- `render_artifact`
- `patch_artifact`
- `lint_artifact`
- `export_artifact`
- `list_artifacts`

It serves these MCP resources:

- `ui://web-gui/runtime/v0.1.css`
- `ui://web-gui/runtime/v0.1.js`
- `ui://web-gui/artifacts/{artifact_id}`

## Install Locally

Use Python 3.11+.

```bash
cd /Users/hzuo/src/web-gui-mcp
python3.11 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

Quick validation:

```bash
cd /Users/hzuo/src/web-gui-mcp
.venv/bin/python -m pytest
.venv/bin/ruff check .
.venv/bin/python scripts/render_gallery.py
```

Generated review gallery:

```text
/Users/hzuo/src/web-gui-mcp/demo/index.html
```

## Connect To Claude Code

Claude Code supports local stdio MCP servers with `claude mcp add`.

Recommended user-scoped install:

```bash
claude mcp add --scope user --transport stdio web-gui-mcp -- /Users/hzuo/src/web-gui-mcp/.venv/bin/web-gui-mcp
claude mcp get web-gui-mcp
```

Project-scoped install from inside a target project:

```bash
claude mcp add --scope project --transport stdio web-gui-mcp -- /Users/hzuo/src/web-gui-mcp/.venv/bin/web-gui-mcp
```

Equivalent JSON form:

```bash
claude mcp add-json web-gui-mcp '{"type":"stdio","command":"/Users/hzuo/src/web-gui-mcp/.venv/bin/web-gui-mcp","args":[]}'
```

Inside Claude Code, run `/mcp` to confirm the server connected.

Reference: https://code.claude.com/docs/en/mcp

## Connect To Cursor

Cursor uses `mcp.json` for MCP configuration. For project-local setup, create
`.cursor/mcp.json` in the project where Cursor should use this server:

```json
{
  "mcpServers": {
    "web-gui-mcp": {
      "command": "/Users/hzuo/src/web-gui-mcp/.venv/bin/web-gui-mcp",
      "args": []
    }
  }
}
```

For a portable macOS user-path variant:

```json
{
  "mcpServers": {
    "web-gui-mcp": {
      "command": "${userHome}/src/web-gui-mcp/.venv/bin/web-gui-mcp",
      "args": []
    }
  }
}
```

Cursor CLI verification:

```bash
cursor-agent mcp list
cursor-agent mcp list-tools web-gui-mcp
```

Reference: https://docs.cursor.com/context/model-context-protocol

## What An Agent Should Do

If the user asks for a visual artifact, interactive review surface, comparison,
prototype, report, handoff, or explainer, prefer this server over writing raw HTML by
hand.

Recommended flow:

1. Call `search_artifact_patterns` if you are unsure which pattern fits.
2. Call `get_artifact_schema` for the chosen pattern.
3. Build a compact declarative `ArtifactSpec`; do not include arbitrary JavaScript,
   raw CSS, inline event handlers, or untrusted raw HTML.
4. Call `lint_artifact` before rendering when the spec is complex or generated from
   ambiguous user input.
5. Call `render_artifact`.
6. Prefer `delivery = "resource_only"` or `delivery = "mcp_app"` for large artifacts.
   Use `delivery = "static_html"` only when the caller explicitly needs the full HTML.
7. If the user asks for an edit to an existing artifact, call `patch_artifact` instead
   of recreating from scratch.
8. If the user needs a text export, call `export_artifact`.

When reporting results to the user, summarize the artifact and provide the returned
`ui://web-gui/artifacts/{artifact_id}` URI when available. Do not paste large HTML into
chat unless explicitly requested.

## Pattern Selection

Use `v = "0.2"` for Chrome-first rich surfaces. Good defaults:

- `approach_comparison`: compare options with recommendation signals.
- `visual_direction_board`: review visual directions or UI concepts.
- `implementation_handoff`: give engineering steps, files, risks, and acceptance.
- `pr_review_workspace`: inspect PR risks, diffs, findings, and actions.
- `module_map`: explain system modules and dependencies.
- `design_system_reference`: document tokens, components, and rules.
- `component_variant_matrix`: compare component states and variants.
- `animation_tuner`: tune deterministic animation presets.
- `clickable_flow`: show a small navigable product flow.
- `diagram_sheet` or `annotated_flowchart`: explain system/process relationships.
- `slide_deck`: produce presentation-like artifact pages.
- `feature_explainer` or `concept_explainer`: explain a feature or concept.
- `status_report` or `incident_report`: summarize operational status.
- `triage_board`: group work items into draggable columns.
- `feature_flag_editor`: show dependency-aware toggles.
- `prompt_tuner`: edit a prompt template with live variable preview.

Use `v = "0.1"` only for compatibility with existing static examples.

## Safety Contract

The server is intentionally conservative:

- Escapes model-provided text.
- Treats `html_preview` as escaped text by default.
- Prevents `</script>` breakout in embedded JSON state.
- Uses deterministic renderer/runtime code only.
- Does not execute model-generated JavaScript.
- Sandboxed prototype/editor sections use `<iframe sandbox="allow-scripts">` without
  `allow-same-origin`.

If a user asks for arbitrary JS, arbitrary CSS, remote scripts, external network
assets, or unescaped raw HTML, do not put that content into the spec. Represent the
intent declaratively with supported sections instead.

## Development Notes

Important local files:

- `src/web_gui_mcp/schema/artifact.py`: ArtifactSpec and section schemas.
- `src/web_gui_mcp/render/sections.py`: section renderers.
- `src/web_gui_mcp/render/css.py`: deterministic artifact CSS.
- `src/web_gui_mcp/render/runtime.py`: deterministic browser interactions.
- `src/web_gui_mcp/mcp_tools.py`: MCP tool handlers.
- `examples/`: example specs.
- `tests/`: schema, render, security, tools, export, and Chromium smoke coverage.

Before committing behavior changes:

```bash
.venv/bin/python -m pytest
.venv/bin/ruff check .
for f in examples/*.json examples/v0_2/*.json; do
  .venv/bin/python scripts/render_example.py "$f" "/tmp/web-gui-$(basename "$f" .json).html" >/dev/null
done
```

