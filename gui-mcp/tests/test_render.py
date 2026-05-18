from __future__ import annotations

import json

from gui2_artifact_mcp.render.artifact import render_artifact_to_html
from gui2_artifact_mcp.schema.artifact import ArtifactSpec
from gui2_artifact_mcp.schema.tool_io import RenderOptions

from .conftest import example_paths


def test_all_examples_render_complete_html() -> None:
    for path in example_paths():
        spec = ArtifactSpec.model_validate(json.loads(path.read_text(encoding="utf-8")))
        rendered = render_artifact_to_html(spec)
        assert rendered.html.startswith("<!doctype html>")
        assert "<main class=\"gui2-shell\">" in rendered.html
        assert f"<title>{spec.title}</title>" in rendered.html
        assert rendered.byte_size == len(rendered.html.encode("utf-8"))


def test_html_preview_is_escaped_by_default() -> None:
    spec = ArtifactSpec.model_validate(
        json.loads((example_paths()[1]).read_text(encoding="utf-8"))
    )
    if spec.artifact != "design_variant_grid":
        spec = ArtifactSpec.model_validate(
            json.loads(
                next(path for path in example_paths() if path.name == "design_variant_grid.json").read_text(
                    encoding="utf-8"
                )
            )
        )
    html = render_artifact_to_html(spec).html
    assert "&lt;button onclick=&quot;alert(1)&quot;&gt;Preview&lt;/button&gt;" in html
    assert '<button onclick="alert(1)">Preview</button>' not in html


def test_json_state_prevents_script_breakout() -> None:
    spec = ArtifactSpec.model_validate(
        {
            "v": "0.1",
            "artifact": "implementation_plan",
            "title": "</script><script>alert(1)</script>",
            "sections": [
                {
                    "kind": "narrative",
                    "title": "Attack",
                    "body": "</script><script>alert(1)</script>",
                }
            ],
        }
    )
    html = render_artifact_to_html(spec).html
    assert "</script><script>alert(1)</script>" not in html
    assert "\\u003c/script\\u003e\\u003cscript\\u003ealert(1)\\u003c/script\\u003e" in html
    assert "&lt;/script&gt;&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert html.count("<script") == 1


def test_local_runtime_is_known_static_script() -> None:
    spec = ArtifactSpec.model_validate(
        {
            "v": "0.1",
            "artifact": "custom_editor",
            "title": "Runtime",
            "sections": [{"kind": "summary", "items": [{"label": "A", "value": "B"}]}],
            "actions": [{"kind": "copy_as_json", "label": "Copy JSON"}],
        }
    )
    html = render_artifact_to_html(
        spec,
        RenderOptions(interactivity="local", include_runtime=True),
    ).html
    assert "data-gui2-action=\"copy-json\"" in html
    assert "document.addEventListener" in html
