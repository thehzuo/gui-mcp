from __future__ import annotations

import json

from gui2_artifact_mcp.render.css import render_css
from gui2_artifact_mcp.render.runtime import render_runtime_tag
from gui2_artifact_mcp.render.sections import render_actions, render_section, render_source_list
from gui2_artifact_mcp.schema.artifact import ArtifactSpec, SourceListSection
from gui2_artifact_mcp.schema.tool_io import RenderedArtifact, RenderOptions
from gui2_artifact_mcp.store.ids import artifact_id_for_spec
from gui2_artifact_mcp.util.escape import attr, h, safe_json_script
from gui2_artifact_mcp.util.size import byte_size


def render_artifact_to_html(spec: ArtifactSpec, options: RenderOptions | None = None) -> RenderedArtifact:
    options = options or RenderOptions(density=spec.density, theme=spec.theme)
    include_runtime = options.include_runtime or options.interactivity != "none" or spec.v == "0.2"
    warnings: list[str] = []
    if options.interactivity == "host_intents":
        warnings.append("host_intents interactivity is a v0.1 stub using postMessage.")
    if options.allow_trusted_html_preview:
        warnings.append("allow_trusted_html_preview bypasses escaped preview rendering.")

    sections_html = "\n".join(render_section(section, options) for section in spec.sections)
    if spec.sources and not any(section.kind == "source_list" for section in spec.sections):
        sections_html += "\n" + render_source_list(SourceListSection(kind="source_list", sources=spec.sources))

    state = json.dumps(
        spec.model_dump(mode="json", by_alias=True),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    state_json = safe_json_script(state)
    artifact_id = artifact_id_for_spec(spec)
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="{_csp(include_runtime)}">
  <title>{h(spec.title)}</title>
  <style>{render_css(theme=options.theme, density=options.density)}</style>
</head>
<body data-gui2-artifact="{attr(spec.artifact)}" data-gui2-id="{attr(artifact_id)}">
  <script id="artifact-state" type="application/json">{state_json}</script>
  <main class="gui2-shell">
    {render_header(spec)}
    {sections_html}
    {render_actions(spec.actions, options)}
  </main>
  {render_runtime_tag(include_runtime)}
</body>
</html>"""
    return RenderedArtifact(
        artifact_id=artifact_id,
        html=html,
        resource_uri=None,
        byte_size=byte_size(html),
        warnings=warnings,
    )


def render_header(spec: ArtifactSpec) -> str:
    subtitle = f'<p class="gui2-subtitle">{h(spec.subtitle)}</p>' if spec.subtitle else ""
    return (
        '<header class="gui2-header">'
        '<div class="gui2-kicker">'
        f'<span class="gui2-badge">{h(spec.artifact.replace("_", " "))}</span>'
        f'<span>{h(spec.v)}</span>'
        f'<span>{h(spec.audience)}</span>'
        f'<span>{h(spec.density)}</span>'
        "</div>"
        f"<h1>{h(spec.title)}</h1>"
        f"{subtitle}</header>"
    )


def _csp(include_runtime: bool) -> str:
    script_src = "'unsafe-inline'" if include_runtime else "'none'"
    return (
        "default-src 'none'; "
        "img-src data:; "
        "style-src 'unsafe-inline'; "
        f"script-src {script_src}; "
        "connect-src 'none'; "
        "frame-ancestors *; "
        "base-uri 'none'; "
        "form-action 'none'"
    )
