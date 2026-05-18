from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from gui2_artifact_mcp.schema.artifact import ArtifactSpec
from gui2_artifact_mcp.schema.tool_io import PatternSummary


@dataclass(frozen=True)
class ArtifactPattern:
    id: str
    name: str
    use_case: str
    description: str
    best_for: list[str]
    token_cost: str
    guidance: list[str]
    example_minimal: dict[str, Any]

    def summary(self) -> PatternSummary:
        return PatternSummary(
            id=self.id,
            name=self.name,
            use_case=self.use_case,
            description=self.description,
            best_for=self.best_for,
            token_cost=self.token_cost,  # type: ignore[arg-type]
        )


PATTERNS: dict[str, ArtifactPattern] = {
    "implementation_plan": ArtifactPattern(
        id="implementation_plan",
        name="Implementation Plan",
        use_case="planning",
        description="Engineering plans, migration plans, and agent work plans.",
        best_for=["phased delivery", "risk tracking", "engineering coordination"],
        token_cost="low",
        guidance=[
            "Start with summary items for scope, risk, and status.",
            "Use timeline for phases and checklist for concrete done criteria.",
            "Use matrix for risks or tradeoffs.",
        ],
        example_minimal={
            "v": "0.1",
            "artifact": "implementation_plan",
            "title": "MVP Implementation Plan",
            "sections": [
                {
                    "kind": "summary",
                    "items": [{"label": "Scope", "value": "Renderer MVP", "tone": "info"}],
                },
                {"kind": "checklist", "title": "Done", "items": [{"text": "Tests pass"}]},
            ],
        },
    ),
    "code_review_explainer": ArtifactPattern(
        id="code_review_explainer",
        name="Code Review Explainer",
        use_case="code_review",
        description="PR reviews, bug-risk summaries, and implementation audits.",
        best_for=["review findings", "annotated diffs", "bug risk communication"],
        token_cost="medium",
        guidance=[
            "Lead with findings and severity.",
            "Use diff_review for changed files and checklist for remediation.",
            "Keep code blocks focused on the risky region.",
        ],
        example_minimal={
            "v": "0.1",
            "artifact": "code_review_explainer",
            "title": "Review Summary",
            "sections": [
                {
                    "kind": "summary",
                    "items": [{"label": "Findings", "value": "1 high risk", "tone": "danger"}],
                },
                {
                    "kind": "diff_review",
                    "title": "Diff",
                    "files": [
                        {
                            "path": "app.py",
                            "hunks": [
                                {
                                    "lines": [
                                        {"type": "remove", "old_line": 1, "text": "return None"},
                                        {"type": "add", "new_line": 1, "text": "return result"},
                                    ]
                                }
                            ],
                        }
                    ],
                },
            ],
        },
    ),
    "design_variant_grid": ArtifactPattern(
        id="design_variant_grid",
        name="Design Variant Grid",
        use_case="design",
        description="Compare UI directions, product concepts, and design system options.",
        best_for=["variant comparison", "recommendations", "tradeoff framing"],
        token_cost="medium",
        guidance=[
            "Use one variant card per direction.",
            "Use comparison for decision criteria.",
            "Keep html_preview as text unless trusted rendering is explicitly enabled.",
        ],
        example_minimal={
            "v": "0.1",
            "artifact": "design_variant_grid",
            "title": "Variant Options",
            "sections": [
                {
                    "kind": "variant_grid",
                    "title": "Directions",
                    "variants": [
                        {"id": "a", "name": "Dense", "description": "Compact operational layout"},
                        {"id": "b", "name": "Guided", "description": "Step-by-step layout"},
                    ],
                }
            ],
        },
    ),
    "research_report": ArtifactPattern(
        id="research_report",
        name="Research Report",
        use_case="research",
        description="Compact synthesis with evidence, tables, timelines, and sources.",
        best_for=["research synthesis", "evidence review", "source-backed summaries"],
        token_cost="medium",
        guidance=[
            "Use summary for conclusions.",
            "Use tables for evidence and source_list for attribution.",
            "Separate facts from recommendations.",
        ],
        example_minimal={
            "v": "0.1",
            "artifact": "research_report",
            "title": "Research Synthesis",
            "sections": [
                {
                    "kind": "summary",
                    "items": [{"label": "Conclusion", "value": "Proceed", "tone": "good"}],
                },
                {"kind": "narrative", "title": "Notes", "body": "Evidence summary."},
            ],
        },
    ),
    "custom_editor": ArtifactPattern(
        id="custom_editor",
        name="Custom Editor",
        use_case="editor",
        description="One-off structured editing surfaces with local state export.",
        best_for=["triage boards", "small editable tables", "structured user feedback"],
        token_cost="high",
        guidance=[
            "Use editable_table for row-oriented data.",
            "Use board for grouped cards.",
            "Add copy actions so edited state can return to the agent loop.",
        ],
        example_minimal={
            "v": "0.1",
            "artifact": "custom_editor",
            "title": "Triage Editor",
            "sections": [
                {
                    "kind": "editable_table",
                    "title": "Rows",
                    "columns": [{"key": "task", "label": "Task", "input": "text"}],
                    "rows": [{"task": "Review spec"}],
                }
            ],
            "actions": [{"kind": "copy_as_json", "label": "Copy JSON"}],
        },
    ),
}


def search_patterns(query: str = "", use_case: str | None = None, max_results: int = 5) -> list[PatternSummary]:
    terms = query.casefold().split()
    results: list[ArtifactPattern] = []
    for pattern in PATTERNS.values():
        if use_case and pattern.use_case != use_case:
            continue
        haystack = " ".join(
            [pattern.id, pattern.name, pattern.description, pattern.use_case, *pattern.best_for]
        ).casefold()
        if terms and not all(term in haystack for term in terms):
            continue
        results.append(pattern)
    return [pattern.summary() for pattern in results[:max_results]]


def get_pattern(pattern_id: str) -> ArtifactPattern:
    try:
        return PATTERNS[pattern_id]
    except KeyError as exc:
        raise ValueError(f"Unknown artifact pattern: {pattern_id}") from exc


def artifact_schema(detail: str = "minimal") -> dict[str, Any]:
    schema = ArtifactSpec.model_json_schema()
    if detail == "full":
        return schema
    return {
        "title": schema.get("title"),
        "type": schema.get("type"),
        "required": schema.get("required", []),
        "properties": schema.get("properties", {}),
    }
