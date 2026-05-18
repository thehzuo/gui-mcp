from __future__ import annotations

import json

from gui2_artifact_mcp.mcp_resources import artifact_resource_handler
from gui2_artifact_mcp.mcp_tools import (
    export_artifact_handler,
    get_artifact_schema_handler,
    lint_artifact_handler,
    list_artifacts_handler,
    patch_artifact_handler,
    render_artifact_handler,
    search_artifact_patterns_handler,
)
from gui2_artifact_mcp.schema.artifact import ArtifactSpec
from gui2_artifact_mcp.schema.tool_io import (
    ExportArtifactInput,
    GetArtifactSchemaInput,
    JsonPatchOp,
    LintArtifactInput,
    ListArtifactsInput,
    PatchArtifactInput,
    RenderArtifactInput,
    SearchArtifactPatternsInput,
)
from gui2_artifact_mcp.store.memory import MemoryArtifactStore


def _spec() -> ArtifactSpec:
    return ArtifactSpec.model_validate(
        {
            "v": "0.1",
            "artifact": "implementation_plan",
            "title": "Tool Spec",
            "sections": [
                {
                    "kind": "summary",
                    "items": [{"label": "Status", "value": "Draft", "tone": "info"}],
                }
            ],
        }
    )


def test_pattern_search_and_schema() -> None:
    found = search_artifact_patterns_handler(
        SearchArtifactPatternsInput(query="review", use_case="code_review")
    )
    assert [pattern.id for pattern in found.patterns] == ["code_review_explainer"]
    schema = get_artifact_schema_handler(GetArtifactSchemaInput(pattern_id="implementation_plan"))
    assert schema.example_minimal["artifact"] == "implementation_plan"
    assert "properties" in schema.schema_


def test_render_list_resource_and_export() -> None:
    store = MemoryArtifactStore()
    output = render_artifact_handler(
        RenderArtifactInput(spec=_spec(), delivery="mcp_app"),
        store,
    )
    assert output.html is None
    assert output.resource_uri == f"ui://gui2/artifacts/{output.artifact_id}"
    assert output.byte_size > 1000

    listed = list_artifacts_handler(ListArtifactsInput(), store)
    assert [item.artifact_id for item in listed.artifacts] == [output.artifact_id]

    html = artifact_resource_handler(output.artifact_id, store)
    assert "Tool Spec" in html

    exported_json = export_artifact_handler(
        ExportArtifactInput(artifact_id=output.artifact_id, format="json"),
        store,
    )
    assert json.loads(exported_json.content)["title"] == "Tool Spec"
    exported_markdown = export_artifact_handler(
        ExportArtifactInput(artifact_id=output.artifact_id, format="markdown"),
        store,
    )
    assert "# Tool Spec" in exported_markdown.content
    exported_prompt = export_artifact_handler(
        ExportArtifactInput(artifact_id=output.artifact_id, format="prompt"),
        store,
    )
    assert "ArtifactSpec JSON" in exported_prompt.content


def test_static_html_delivery_returns_html() -> None:
    store = MemoryArtifactStore()
    output = render_artifact_handler(
        RenderArtifactInput(spec=_spec(), delivery="static_html"),
        store,
    )
    assert output.html is not None
    assert output.resource_uri is None


def test_patch_artifact_revalidates_and_increments_revision() -> None:
    store = MemoryArtifactStore()
    rendered = render_artifact_handler(RenderArtifactInput(spec=_spec()), store)
    patched = patch_artifact_handler(
        PatchArtifactInput(
            artifact_id=rendered.artifact_id,
            delivery="static_html",
            delta=[
                JsonPatchOp(op="replace", path="/title", value="Patched Spec"),
                JsonPatchOp(op="replace", path="/sections/0/items/0/value", value="Ready"),
            ],
        ),
        store,
    )
    assert patched.revision == 2
    assert patched.html is not None
    assert "Patched Spec" in patched.html
    assert store.get(rendered.artifact_id).spec.title == "Patched Spec"  # type: ignore[union-attr]


def test_lint_artifact_reports_security_issues() -> None:
    spec = ArtifactSpec.model_validate(
        {
            "v": "0.1",
            "artifact": "implementation_plan",
            "title": "Risky",
            "sections": [
                {
                    "kind": "narrative",
                    "title": "Body",
                    "body": "<img src=x onerror=alert(1)>",
                }
            ],
        }
    )
    spec_lint = lint_artifact_handler(LintArtifactInput(spec=spec, checks=["security"]))
    assert spec_lint.ok
    assert spec_lint.issues[0].severity == "warning"

    html_lint = lint_artifact_handler(
        LintArtifactInput(html="<img src=x onerror=alert(1)>", checks=["security"])
    )
    assert not html_lint.ok
    assert html_lint.issues[0].severity == "error"
