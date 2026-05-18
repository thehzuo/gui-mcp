from __future__ import annotations

from gui2_artifact_mcp.render.artifact import render_artifact_to_html
from gui2_artifact_mcp.schema.artifact import ArtifactSpec


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
