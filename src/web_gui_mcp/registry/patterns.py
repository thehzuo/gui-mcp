from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from web_gui_mcp.schema.artifact import ArtifactSpec
from web_gui_mcp.schema.tool_io import PatternSummary


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


def _v2_pattern(
    pattern_id: str,
    name: str,
    use_case: str,
    description: str,
    best_for: list[str],
    section: dict[str, Any],
    token_cost: str = "medium",
) -> ArtifactPattern:
    return ArtifactPattern(
        id=pattern_id,
        name=name,
        use_case=use_case,
        description=description,
        best_for=best_for,
        token_cost=token_cost,
        guidance=[
            "Use v0.2 when the artifact needs Chrome-first interaction or richer layout.",
            "Keep content semantic; the renderer owns HTML, CSS, and runtime behavior.",
            "Use declarative sections instead of raw HTML, CSS, or JavaScript.",
        ],
        example_minimal={
            "v": "0.2",
            "artifact": pattern_id,
            "title": name,
            "sections": [section],
        },
    )


PATTERNS.update(
    {
        "approach_comparison": _v2_pattern(
            "approach_comparison",
            "Approach Comparison",
            "planning",
            "Compare implementation approaches with filters, tradeoffs, and decision notes.",
            ["architecture choices", "tradeoff reviews", "technical options"],
            {
                "kind": "filterable_collection",
                "title": "Approaches",
                "items": [
                    {
                        "id": "safe",
                        "title": "Safe incremental",
                        "body": "Small additive changes with low migration risk.",
                        "tags": ["safe", "incremental"],
                    }
                ],
            },
        ),
        "visual_direction_board": _v2_pattern(
            "visual_direction_board",
            "Visual Direction Board",
            "design",
            "Review multiple product or UI directions as a studio sheet.",
            ["visual exploration", "design critiques", "direction selection"],
            {
                "kind": "component_matrix",
                "title": "Directions",
                "component": "Empty state",
                "variants": [
                    {
                        "id": "studio",
                        "name": "Studio sheet",
                        "state": "default",
                        "intent": "review",
                        "notes": "Dense, copyable review board.",
                    }
                ],
            },
        ),
        "implementation_handoff": _v2_pattern(
            "implementation_handoff",
            "Implementation Handoff",
            "planning",
            "A handoff plan with flow, risky code, milestones, and acceptance checks.",
            ["handoffs", "agent work packets", "implementation sequencing"],
            {
                "kind": "split_view",
                "title": "Handoff",
                "left_title": "Build",
                "left_body": "Implement the additive schema and runtime.",
                "right_title": "Verify",
                "right_body": "Run Python and Chrome smoke tests.",
            },
        ),
        "pr_review_workspace": _v2_pattern(
            "pr_review_workspace",
            "PR Review Workspace",
            "code_review",
            "Review diffs with jumpable findings, severity, filters, and annotations.",
            ["review findings", "diff triage", "risk scans"],
            {
                "kind": "tabs",
                "title": "Review",
                "tabs": [
                    {"id": "findings", "label": "Findings", "body": "Lead with actionable issues."},
                    {"id": "diff", "label": "Diff", "body": "Inspect the risky hunk."},
                ],
            },
        ),
        "pr_author_writeup": _v2_pattern(
            "pr_author_writeup",
            "PR Author Writeup",
            "code_review",
            "Explain a pull request from the author's perspective for reviewers.",
            ["reviewer onboarding", "before/after tours", "focus areas"],
            {
                "kind": "tabs",
                "title": "Reviewer Tour",
                "tabs": [
                    {"id": "why", "label": "Why", "body": "Motivation and product context."},
                    {"id": "files", "label": "Files", "body": "File-by-file review map."},
                ],
            },
        ),
        "module_map": _v2_pattern(
            "module_map",
            "Module Map",
            "code_understanding",
            "Explain an unfamiliar module with entry points, hot paths, and dependencies.",
            ["codebase orientation", "dependency maps", "hot path explanation"],
            {
                "kind": "inspector_diagram",
                "title": "Module Flow",
                "nodes": [
                    {"id": "entry", "label": "Entry", "description": "Request enters here.", "x": 20, "y": 45},
                    {"id": "core", "label": "Core", "description": "Business logic.", "x": 65, "y": 45},
                ],
                "edges": [{"from": "entry", "to": "core"}],
            },
        ),
        "design_system_reference": _v2_pattern(
            "design_system_reference",
            "Design System Reference",
            "design_system",
            "Render copyable design tokens, type scale, and component notes.",
            ["token audits", "style references", "implementation specs"],
            {
                "kind": "token_sheet",
                "title": "Tokens",
                "groups": [{"title": "Color", "tokens": [{"name": "accent", "value": "#C23B22"}]}],
            },
        ),
        "component_variant_matrix": _v2_pattern(
            "component_variant_matrix",
            "Component Variant Matrix",
            "design_system",
            "Show all states, sizes, and intents of a component in one sheet.",
            ["component QA", "variant reviews", "state coverage"],
            {
                "kind": "component_matrix",
                "title": "Button Matrix",
                "component": "Button",
                "variants": [{"id": "primary", "name": "Primary", "state": "default", "intent": "submit"}],
            },
        ),
        "animation_tuner": _v2_pattern(
            "animation_tuner",
            "Animation Tuner",
            "prototyping",
            "Tune a single animation with deterministic controls and replay.",
            ["motion review", "easing comparison", "micro-interaction tuning"],
            {
                "kind": "animation_controls",
                "title": "Transition",
                "presets": [{"id": "snap", "label": "Snap", "duration_ms": 220}],
            },
        ),
        "clickable_flow": _v2_pattern(
            "clickable_flow",
            "Clickable Flow",
            "prototyping",
            "Model a multi-screen interaction without generated JavaScript.",
            ["flow validation", "prototype walkthroughs", "interaction critique"],
            {
                "kind": "prototype_flow",
                "title": "Flow",
                "screens": [
                    {"id": "start", "title": "Start", "body": "Choose a path."},
                    {"id": "done", "title": "Done", "body": "Confirm the result."},
                ],
                "links": [{"from": "start", "to": "done", "label": "Continue"}],
            },
        ),
        "diagram_sheet": _v2_pattern(
            "diagram_sheet",
            "Diagram Sheet",
            "diagrams",
            "Collect copyable figures and diagrams in one generated sheet.",
            ["blog figures", "architecture sketches", "diagram iteration"],
            {
                "kind": "copyable_asset_grid",
                "title": "Figures",
                "assets": [{"id": "fig1", "title": "Flow", "kind": "svg", "content": "<svg></svg>"}],
            },
        ),
        "annotated_flowchart": _v2_pattern(
            "annotated_flowchart",
            "Annotated Flowchart",
            "diagrams",
            "Clickable process diagrams with side inspection for timings and failure paths.",
            ["deploy pipelines", "system flows", "process explanation"],
            {
                "kind": "inspector_diagram",
                "title": "Pipeline",
                "nodes": [{"id": "build", "label": "Build", "description": "Compile assets."}],
            },
        ),
        "slide_deck": _v2_pattern(
            "slide_deck",
            "Slide Deck",
            "decks",
            "A Chrome-first one-file deck with keyboard navigation.",
            ["weekly updates", "executive walkthroughs", "design reviews"],
            {
                "kind": "slide_deck",
                "title": "Deck",
                "slides": [{"id": "one", "title": "One", "body": "Opening slide."}],
            },
        ),
        "feature_explainer": _v2_pattern(
            "feature_explainer",
            "Feature Explainer",
            "research",
            "Explain how a repo feature works with tabs, request paths, and snippets.",
            ["feature research", "architecture explanation", "onboarding"],
            {
                "kind": "tabs",
                "title": "How it works",
                "tabs": [{"id": "path", "label": "Path", "body": "Request path steps."}],
            },
        ),
        "concept_explainer": _v2_pattern(
            "concept_explainer",
            "Concept Explainer",
            "research",
            "Teach a technical concept with a small deterministic model and glossary.",
            ["teaching", "concept review", "interactive explanation"],
            {
                "kind": "inspector_diagram",
                "title": "Concept Model",
                "nodes": [{"id": "idea", "label": "Idea", "description": "Inspect the concept."}],
            },
        ),
        "status_report": _v2_pattern(
            "status_report",
            "Status Report",
            "reports",
            "Summarize shipped, slipped, blocked, and next work with small charts.",
            ["weekly status", "team updates", "executive skims"],
            {
                "kind": "chart_panel",
                "title": "Work",
                "data": [{"label": "Shipped", "value": 7, "tone": "good"}],
            },
        ),
        "incident_report": _v2_pattern(
            "incident_report",
            "Incident Report",
            "reports",
            "Minute-by-minute postmortems with logs, impact, and follow-up work.",
            ["postmortems", "incident timelines", "ops reports"],
            {
                "kind": "log_timeline",
                "title": "Timeline",
                "events": [{"timestamp": "12:01", "level": "warning", "message": "Error rate rose."}],
            },
        ),
        "triage_board": _v2_pattern(
            "triage_board",
            "Triage Board",
            "editor",
            "Drag/reorder work across Now, Next, Later, and Cut.",
            ["ticket triage", "planning boards", "priority sorting"],
            {
                "kind": "board",
                "title": "Triage",
                "columns": [{"id": "now", "title": "Now", "cards": [{"id": "a", "title": "Fix A"}]}],
            },
            token_cost="high",
        ),
        "feature_flag_editor": _v2_pattern(
            "feature_flag_editor",
            "Feature Flag Editor",
            "editor",
            "Toggle flags with dependency warnings and copyable diffs.",
            ["flag review", "release gating", "configuration edits"],
            {
                "kind": "dependency_toggle_list",
                "title": "Flags",
                "toggles": [{"id": "base", "label": "Base flag", "enabled": True}],
            },
            token_cost="high",
        ),
        "prompt_tuner": _v2_pattern(
            "prompt_tuner",
            "Prompt Tuner",
            "editor",
            "Edit prompt variables and preview rendered sample prompts live.",
            ["prompt iteration", "template tuning", "support response testing"],
            {
                "kind": "prompt_tuner",
                "title": "Prompt",
                "template": "Hello {{name}}",
                "variables": [{"name": "name", "label": "Name", "value": "Ada"}],
            },
            token_cost="high",
        ),
    }
)


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
