# GUI 2.0 Artifact MCP Design

This implementation follows the local design document supplied for the MVP:
`/Users/hzuo/Downloads/gui2_artifact_mcp_python_design_doc (1).md`.

The implemented scope is the v0.1 static-first Python port:

- Python 3.11+
- official MCP Python SDK with FastMCP
- Pydantic v2 schema validation
- deterministic single-file HTML rendering
- in-memory artifact storage
- `ui://gui2/artifacts/{artifact_id}` resource-shaped delivery
- pytest coverage for schema, rendering, security, patching, tools, and exports

The v0.2 upgrade adds Chrome-first Studio Sheet artifacts, sandboxed prototype/editor
sections, deterministic interaction primitives, twenty richer pattern families, and
Playwright Chromium smoke coverage.
