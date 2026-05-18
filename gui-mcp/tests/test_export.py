from __future__ import annotations

from gui2_artifact_mcp.render.markdown_export import export_markdown
from gui2_artifact_mcp.render.prompt_export import export_prompt
from gui2_artifact_mcp.schema.artifact import ArtifactSpec


def test_markdown_and_prompt_exports_are_useful() -> None:
    spec = ArtifactSpec.model_validate(
        {
            "v": "0.1",
            "artifact": "research_report",
            "title": "Export Spec",
            "sections": [
                {
                    "kind": "table",
                    "title": "Rows",
                    "columns": [{"key": "name", "label": "Name"}],
                    "rows": [{"name": "Alpha"}],
                }
            ],
        }
    )
    markdown = export_markdown(spec)
    assert "# Export Spec" in markdown
    assert "| Name |" in markdown
    prompt = export_prompt(spec)
    assert "ArtifactSpec JSON" in prompt
    assert '"artifact": "research_report"' in prompt
