from __future__ import annotations

from web_gui_mcp.render.artifact import render_artifact_to_html
from web_gui_mcp.schema.artifact import ArtifactSpec


def test_model_text_is_escaped_across_text_and_attributes() -> None:
    spec = ArtifactSpec.model_validate(
        {
            "v": "0.1",
            "artifact": "research_report",
            "title": "<script>alert(1)</script>",
            "sections": [
                {
                    "kind": "source_list",
                    "title": "Sources",
                    "sources": [
                        {
                            "title": "<img src=x onerror=alert(1)>",
                            "url": "javascript:alert(1)",
                            "note": "</script><script>alert(1)</script>",
                        }
                    ],
                }
            ],
        }
    )
    html = render_artifact_to_html(spec).html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert "href=\"javascript:alert(1)\"" not in html
    assert "</script><script>alert(1)</script>" not in html


def test_no_model_generated_inline_handlers_are_rendered() -> None:
    spec = ArtifactSpec.model_validate(
        {
            "v": "0.1",
            "artifact": "design_variant_grid",
            "title": "Preview",
            "sections": [
                {
                    "kind": "variant_grid",
                    "title": "Variants",
                    "variants": [
                        {
                            "id": "x",
                            "name": "X",
                            "description": "Preview",
                            "html_preview": "<a href=\"javascript:alert(1)\" onclick=\"alert(2)\">bad</a>",
                        }
                    ],
                }
            ],
        }
    )
    html = render_artifact_to_html(spec).html
    assert '<a href="javascript:alert(1)" onclick="alert(2)">bad</a>' not in html
    assert "&lt;a href=&quot;javascript:alert(1)&quot; onclick=&quot;alert(2)&quot;&gt;bad&lt;/a&gt;" in html


def test_v02_sandbox_escapes_model_text_and_script_breakout() -> None:
    spec = ArtifactSpec.model_validate(
        {
            "v": "0.2",
            "artifact": "prompt_tuner",
            "title": "Sandbox attack",
            "sections": [
                {
                    "kind": "prompt_tuner",
                    "title": "Prompt",
                    "template": "</script><script>alert(1)</script> {{name}}",
                    "variables": [
                        {
                            "name": "name",
                            "label": "Name",
                            "value": "<img src=x onerror=alert(1)>",
                        }
                    ],
                }
            ],
        }
    )
    html = render_artifact_to_html(spec).html
    assert "</script><script>alert(1)</script>" not in html
    assert "&amp;lt;/script&amp;gt;&amp;lt;script&amp;gt;alert(1)&amp;lt;/script&amp;gt;" in html
    assert "&amp;lt;img src=x onerror=alert(1)&amp;gt;" in html
    assert "allow-same-origin" not in html


def test_v02_copyable_assets_do_not_render_raw_css_or_html() -> None:
    spec = ArtifactSpec.model_validate(
        {
            "v": "0.2",
            "artifact": "diagram_sheet",
            "title": "Assets",
            "sections": [
                {
                    "kind": "copyable_asset_grid",
                    "title": "Assets",
                    "assets": [
                        {
                            "id": "css",
                            "title": "CSS",
                            "kind": "css",
                            "content": "body{background:url(javascript:alert(1))}</style><script>alert(1)</script>",
                        }
                    ],
                }
            ],
        }
    )
    html = render_artifact_to_html(spec).html
    assert "</style><script>alert(1)</script>" not in html
    assert "&lt;/style&gt;&lt;script&gt;alert(1)&lt;/script&gt;" in html
