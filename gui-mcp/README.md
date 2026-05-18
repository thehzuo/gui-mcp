# gui2-artifact-mcp-py

`gui2-artifact-mcp-py` is a Python MCP server that validates compact `ArtifactSpec`
JSON and renders deterministic, static HTML artifacts. It stores artifacts in memory
and can return either full HTML or an MCP App-style `ui://` resource URI.

## Setup

```bash
uv sync
uv run pytest
uv run python scripts/render_example.py examples/implementation_plan.json /tmp/gui2-plan.html
```

Without `uv`:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
python scripts/render_example.py examples/implementation_plan.json /tmp/gui2-plan.html
```

## Run The MCP Server

```bash
uv run gui2-artifact-mcp
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

- `ui://gui2/runtime/v0.1.css`
- `ui://gui2/runtime/v0.1.js`
- `ui://gui2/artifacts/{artifact_id}`

## Connect To Codex

Add a local MCP server entry to your Codex config, using this repository as `cwd`:

```toml
[mcp_servers.gui2_artifact_mcp]
command = "uv"
args = ["run", "gui2-artifact-mcp"]
cwd = "/Users/hzuo/src/agent-loom/gui-mcp"
startup_timeout_sec = 20
tool_timeout_sec = 60
enabled = true
```

Without `uv`:

```toml
[mcp_servers.gui2_artifact_mcp]
command = "python"
args = ["-m", "gui2_artifact_mcp.server"]
cwd = "/Users/hzuo/src/agent-loom/gui-mcp"
startup_timeout_sec = 20
tool_timeout_sec = 60
enabled = true
```

## Render An Artifact

`render_artifact` accepts a compact semantic spec:

```json
{
  "spec": {
    "v": "0.1",
    "artifact": "implementation_plan",
    "title": "MVP Plan",
    "sections": [
      {
        "kind": "summary",
        "items": [
          { "label": "Status", "value": "Ready", "tone": "good" }
        ]
      }
    ]
  },
  "delivery": "static_html"
}
```

Use `delivery = "mcp_app"` or `delivery = "resource_only"` when you want a stored
`ui://gui2/artifacts/{artifact_id}` URI instead of returning full HTML through the
tool response.

## Safety

- All model-provided text is HTML-escaped.
- `html_preview` is escaped text by default.
- JSON state embedded in `<script type="application/json">` escapes `<`, `>`, `&`,
  U+2028, and U+2029 to prevent `</script>` breakout.
- The renderer does not execute or copy arbitrary model-generated JavaScript.
- CSS, HTML structure, and optional local runtime behavior are deterministic.
