from __future__ import annotations

import json

from web_gui_mcp.render.artifact import render_artifact_to_html
from web_gui_mcp.schema.artifact import ArtifactSpec
from web_gui_mcp.schema.tool_io import RenderOptions

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


def test_v02_includes_runtime_and_sandboxed_iframe() -> None:
    spec = ArtifactSpec.model_validate(
        {
            "v": "0.2",
            "artifact": "clickable_flow",
            "title": "Sandbox",
            "sections": [
                {
                    "kind": "prototype_flow",
                    "title": "Flow",
                    "screens": [
                        {"id": "a", "title": "A", "body": "First"},
                        {"id": "b", "title": "B", "body": "Second"},
                    ],
                    "links": [{"from": "a", "to": "b", "label": "Next"}],
                }
            ],
        }
    )
    html = render_artifact_to_html(spec).html
    assert 'sandbox="allow-scripts"' in html
    assert "allow-same-origin" not in html
    assert "data-prototype-target" in html
    assert 'data-kind="slide_deck"' not in html
    assert "document.addEventListener" in html


def test_v02_sections_render_fallback_content() -> None:
    spec = ArtifactSpec.model_validate(
        {
            "v": "0.2",
            "artifact": "feature_explainer",
            "title": "Fallbacks",
            "sections": [
                {
                    "kind": "tabs",
                    "title": "Tabs",
                    "tabs": [
                        {"id": "one", "label": "One", "body": "Visible if scripts fail."},
                        {"id": "two", "label": "Two", "body": "Also present in the HTML."},
                    ],
                },
                {
                    "kind": "filterable_collection",
                    "title": "Items",
                    "items": [{"id": "a", "title": "Alpha", "body": "Filterable text"}],
                },
            ],
        }
    )
    html = render_artifact_to_html(spec).html
    assert "Visible if scripts fail." in html
    assert "Also present in the HTML." in html
    assert "Filterable text" in html
    assert "data-gui2-filter" in html


def test_v02_log_details_use_native_collapsible() -> None:
    spec = ArtifactSpec.model_validate(
        {
            "v": "0.2",
            "artifact": "incident_report",
            "title": "Incident",
            "sections": [
                {
                    "kind": "log_timeline",
                    "title": "Timeline",
                    "events": [
                        {
                            "timestamp": "12:00",
                            "level": "error",
                            "message": "Failure",
                            "detail": "stack trace",
                        }
                    ],
                }
            ],
        }
    )
    html = render_artifact_to_html(spec).html
    assert "<details>" in html
    assert "<summary>Details</summary>" in html
