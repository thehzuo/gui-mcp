# AGENTS.md

## Project

This repo implements `gui2-artifact-mcp-py`, a Python MCP server that compiles compact
`ArtifactSpec` JSON into rich HTML artifacts and optional MCP App-style resources.

## Commands

- Install: `uv sync`
- Test: `uv run pytest`
- Lint: `uv run ruff check .`
- Dev server: `uv run gui2-artifact-mcp`
- Render example: `uv run python scripts/render_example.py examples/implementation_plan.json /tmp/gui2-plan.html`

## Engineering Rules

- Prefer small pure functions.
- Validate all external inputs with Pydantic.
- Escape all model-provided text before rendering HTML.
- Do not render arbitrary model-provided JavaScript.
- Keep the renderer deterministic.
- Add or update tests for behavior changes.
- Keep dependencies minimal.
- Use `html.escape` or the project escaping helper for text nodes and attributes.
- Use the dedicated helper for JSON embedded inside `<script type="application/json">`.

## Done Means

- Tests pass.
- Example artifacts render.
- Security tests pass.
- README remains accurate.
