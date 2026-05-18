from __future__ import annotations

from typing import Any

from gui2_artifact_mcp.schema.artifact import ArtifactSpec


def export_markdown(spec: ArtifactSpec) -> str:
    lines = [f"# {spec.title}", ""]
    if spec.subtitle:
        lines.extend([spec.subtitle, ""])
    for section in spec.sections:
        title = getattr(section, "title", None) or section.kind.replace("_", " ").title()
        lines.extend([f"## {title}", ""])
        lines.extend(_section_lines(section))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _section_lines(section: Any) -> list[str]:
    kind = section.kind
    if kind == "summary":
        return [f"- **{item.label}:** {item.value}" for item in section.items]
    if kind in {"narrative", "callout"}:
        return [section.body]
    if kind == "checklist":
        return [f"- [{'x' if item.checked else ' '}] {item.text}" for item in section.items]
    if kind in {"table", "editable_table"}:
        header = "| " + " | ".join(column.label for column in section.columns) + " |"
        divider = "| " + " | ".join("---" for _ in section.columns) + " |"
        rows = [
            "| " + " | ".join(str(row.get(column.key, "")) for column in section.columns) + " |"
            for row in section.rows
        ]
        return [header, divider, *rows]
    if kind == "comparison":
        return [f"- **{option.label}:** {option.summary or ''}" for option in section.options]
    if kind == "matrix":
        return [f"- {cell.x} / {cell.y}: {cell.label}" for cell in section.cells]
    if kind == "timeline":
        return [f"- {event.date or event.status}: {event.label}" for event in section.events]
    if kind == "flow":
        node_lines = [f"- {node.id}: {node.label}" for node in section.nodes]
        edge_lines = [f"- {edge.from_} -> {edge.to}" for edge in section.edges]
        return node_lines + edge_lines
    if kind == "code":
        language = section.language or ""
        return [f"```{language}", section.code, "```"]
    if kind == "diff_review":
        return [f"- {file.path}" for file in section.files]
    if kind == "variant_grid":
        return [f"- **{variant.name}:** {variant.description}" for variant in section.variants]
    if kind == "board":
        lines = []
        for column in section.columns:
            lines.append(f"### {column.title}")
            lines.extend(f"- {card.title}" for card in column.cards)
        return lines
    if kind == "source_list":
        return [f"- {source.title}: {source.url or ''}" for source in section.sources]
    if kind == "split_view":
        return [f"### {section.left_title}", section.left_body, f"### {section.right_title}", section.right_body]
    if kind == "tabs":
        return [f"- **{tab.label}:** {tab.body}" for tab in section.tabs]
    if kind == "filterable_collection":
        return [f"- **{item.title}:** {item.body}" for item in section.items]
    if kind == "inspector_diagram":
        return [f"- {node.id}: {node.label} - {node.description}" for node in section.nodes]
    if kind == "prototype_flow":
        return [f"- {screen.id}: {screen.title}" for screen in section.screens]
    if kind == "animation_controls":
        return [f"- {preset.label}: {preset.duration_ms}ms" for preset in section.presets]
    if kind == "token_sheet":
        lines = []
        for group in section.groups:
            lines.append(f"### {group.title}")
            lines.extend(f"- `{token.name}` = `{token.value}`" for token in group.tokens)
        return lines
    if kind == "component_matrix":
        return [f"- {variant.name}: {variant.intent} / {variant.state}" for variant in section.variants]
    if kind == "slide_deck":
        return [f"- {slide.title}: {slide.body}" for slide in section.slides]
    if kind == "chart_panel":
        return [f"- {datum.label}: {datum.value}" for datum in section.data]
    if kind == "log_timeline":
        return [f"- {event.timestamp} [{event.level}] {event.message}" for event in section.events]
    if kind == "dependency_toggle_list":
        return [f"- [{'x' if toggle.enabled else ' '}] {toggle.label}" for toggle in section.toggles]
    if kind == "prompt_tuner":
        return ["```text", section.template, "```"]
    if kind == "copyable_asset_grid":
        return [f"- {asset.title} ({asset.kind})" for asset in section.assets]
    return []
