# web-gui-mcp
`web-gui-mcp` is a Python MCP server that allows your agent to outsource the html generation and rendering. It stores artifacts in memory and can
return either full HTML or an MCP App-style `ui://` resource URI. Inspired by https://thariqs.github.io/html-effectiveness/ but with cost in mind.

Agent/LLM entrypoints:

- [`README.agent.md`](README.agent.md): setup, Claude Code, Cursor, and agent usage guidance.
- [`llms.txt`](llms.txt): concise machine-readable orientation.

The renderer supports the original safe static `v0.1` contract and an additive
Chrome-first `v0.2` contract with richer Studio Sheet layouts, sandboxed prototypes,
and deterministic local interactions.

## Setup

```bash
uv sync
uv run pytest
uv run pytest tests/test_chromium_smoke.py
uv run python scripts/render_example.py examples/implementation_plan.json /tmp/web-gui-plan.html
```

Without `uv`:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
pytest tests/test_chromium_smoke.py
python scripts/render_example.py examples/implementation_plan.json /tmp/web-gui-plan.html
```

The Chromium smoke tests target local Google Chrome/Chromium through Playwright.

## Run The MCP Server

```bash
uv run web-gui-mcp
```

The server exposes:

- `search_artifact_patterns`
- `get_artifact_schema`
- `render_artifact`
- `patch_artifact`
- `lint_artifact`
- `export_artifact`
- `list_artifacts`

It also serves:

- `ui://web-gui/runtime/v0.1.css`
- `ui://web-gui/runtime/v0.1.js`
- `ui://web-gui/artifacts/{artifact_id}`

## Pattern Families

`v0.1` patterns remain supported:

- `implementation_plan`
- `code_review_explainer`
- `design_variant_grid`
- `research_report`
- `custom_editor`

`v0.2` adds Chrome-first artifact families:

- `approach_comparison`
- `visual_direction_board`
- `implementation_handoff`
- `pr_review_workspace`
- `pr_author_writeup`
- `module_map`
- `design_system_reference`
- `component_variant_matrix`
- `animation_tuner`
- `clickable_flow`
- `diagram_sheet`
- `annotated_flowchart`
- `slide_deck`
- `feature_explainer`
- `concept_explainer`
- `status_report`
- `incident_report`
- `triage_board`
- `feature_flag_editor`
- `prompt_tuner`

## v0.2 Interactions

Use `v = "0.2"` when an artifact needs richer local behavior:

- tabs, filters, collapsibles, copy/export buttons
- sliders and replay controls
- keyboard slide navigation
- clickable diagram inspectors
- drag/reorder boards
- dependency-aware toggles
- live prompt-template previews

Prototype and editor surfaces use sandboxed `iframe srcdoc` documents with
`sandbox="allow-scripts"`. The sandbox does not allow same-origin access or network
requests. Model output remains declarative and escaped; only the known renderer
runtime executes.

## Connect To Codex

Add a local MCP server entry to your Codex config, using this repository as `cwd`:

```toml
[mcp_servers.web_gui_mcp]
command = "uv"
args = ["run", "web-gui-mcp"]
cwd = "/Users/hzuo/src/web-gui-mcp"
startup_timeout_sec = 20
tool_timeout_sec = 60
enabled = true
```

Without `uv`:

```toml
[mcp_servers.web_gui_mcp]
command = "python"
args = ["-m", "web_gui_mcp.server"]
cwd = "/Users/hzuo/src/web-gui-mcp"
startup_timeout_sec = 20
tool_timeout_sec = 60
enabled = true
```

## Connect To Claude Code Or Cursor

For Claude Code and Cursor configuration snippets, see [`README.agent.md`](README.agent.md).

## Render An Artifact

`render_artifact` accepts a compact semantic spec:

```json
{
  "spec": {
    "v": "0.2",
    "artifact": "feature_explainer",
    "title": "Rate Limiting Explainer",
    "sections": [
      {
        "kind": "tabs",
        "title": "How it works",
        "tabs": [
          { "id": "tldr", "label": "TL;DR", "body": "Requests are keyed by account and route." },
          { "id": "path", "label": "Path", "body": "Middleware increments usage and emits headers." }
        ]
      }
    ]
  },
  "delivery": "static_html"
}
```

Use `delivery = "mcp_app"` or `delivery = "resource_only"` when you want a stored
`ui://web-gui/artifacts/{artifact_id}` URI instead of returning full HTML through the
tool response.

## Safety

- All model-provided text is HTML-escaped.
- `html_preview` is escaped text by default.
- v0.2 prototype/editor sections use sandboxed iframe `srcdoc` documents.
- Generated interactions use deterministic runtime code; model-generated JavaScript is not allowed.
- JSON state embedded in `<script type="application/json">` escapes `<`, `>`, `&`,
  U+2028, and U+2029 to prevent `</script>` breakout.
- The renderer does not execute or copy arbitrary model-generated JavaScript.
- CSS, HTML structure, and optional local runtime behavior are deterministic.
