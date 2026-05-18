from __future__ import annotations

import json
from typing import Any

from gui2_artifact_mcp.schema.artifact import (
    BoardSection,
    CalloutSection,
    ChecklistSection,
    CodeSection,
    ComparisonSection,
    DiffReviewSection,
    EditableTableSection,
    FlowSection,
    MatrixSection,
    NarrativeSection,
    SourceListSection,
    SummarySection,
    TableSection,
    TimelineSection,
    VariantGridSection,
)
from gui2_artifact_mcp.schema.tool_io import RenderOptions
from gui2_artifact_mcp.util.escape import attr, h, safe_href


def render_section(section: Any, options: RenderOptions) -> str:
    body = _render_section_body(section, options)
    return f'<section class="gui2-section gui2-section-{attr(section.kind)}" data-kind="{attr(section.kind)}">{body}</section>'


def _section_heading(title: str | None) -> str:
    return f"<h2>{h(title)}</h2>" if title else ""


def _render_section_body(section: Any, options: RenderOptions) -> str:
    if isinstance(section, SummarySection):
        return render_summary(section)
    if isinstance(section, NarrativeSection):
        return render_narrative(section)
    if isinstance(section, CalloutSection):
        return render_callout(section)
    if isinstance(section, ChecklistSection):
        return render_checklist(section)
    if isinstance(section, TableSection):
        return render_table(section)
    if isinstance(section, ComparisonSection):
        return render_comparison(section)
    if isinstance(section, MatrixSection):
        return render_matrix(section)
    if isinstance(section, TimelineSection):
        return render_timeline(section)
    if isinstance(section, FlowSection):
        return render_flow(section)
    if isinstance(section, CodeSection):
        return render_code(section)
    if isinstance(section, DiffReviewSection):
        return render_diff_review(section)
    if isinstance(section, VariantGridSection):
        return render_variant_grid(section, options)
    if isinstance(section, EditableTableSection):
        return render_editable_table(section)
    if isinstance(section, BoardSection):
        return render_board(section)
    if isinstance(section, SourceListSection):
        return render_source_list(section)
    raise TypeError(f"Unsupported section type: {type(section).__name__}")


def render_summary(section: SummarySection) -> str:
    cards = []
    for item in section.items:
        cards.append(
            f'<div class="gui2-card gui2-tone-{attr(item.tone)}">'
            f'<div class="gui2-label">{h(item.label)}</div>'
            f'<div class="gui2-value">{h(item.value)}</div>'
            "</div>"
        )
    return _section_heading(section.title) + f'<div class="gui2-grid gui2-summary-grid">{"".join(cards)}</div>'


def render_narrative(section: NarrativeSection) -> str:
    return _section_heading(section.title) + _paragraphs(section.body)


def render_callout(section: CalloutSection) -> str:
    return (
        f'<div class="gui2-callout gui2-tone-{attr(section.tone)}">'
        f"{_section_heading(section.title)}{_paragraphs(section.body)}"
        "</div>"
    )


def render_checklist(section: ChecklistSection) -> str:
    items = []
    for item in section.items:
        checked = " checked" if item.checked else ""
        items.append(
            "<li>"
            f'<input type="checkbox" disabled{checked} aria-label="{attr(item.text)}">'
            f"<span>{h(item.text)}</span>"
            f'<span class="gui2-priority">{h(item.priority)}</span>'
            "</li>"
        )
    return _section_heading(section.title) + f'<ul class="gui2-checklist">{"".join(items)}</ul>'


def render_table(section: TableSection) -> str:
    return _section_heading(section.title) + _table(section.columns, section.rows)


def render_comparison(section: ComparisonSection) -> str:
    cards = []
    for option in section.options:
        attrs = "".join(
            f'<li><span class="gui2-label">{h(key)}</span>: {h(value)}</li>'
            for key, value in option.attributes.items()
        )
        recommendation = (
            f'<span class="gui2-badge">{h(option.recommendation)}</span>'
            if option.recommendation
            else ""
        )
        cards.append(
            '<article class="gui2-card">'
            f"<h3>{h(option.label)} {recommendation}</h3>"
            f"{_paragraphs(option.summary or '')}"
            f'<ul class="gui2-list">{attrs}</ul>'
            "</article>"
        )
    return _section_heading(section.title) + f'<div class="gui2-comparison">{"".join(cards)}</div>'


def render_matrix(section: MatrixSection) -> str:
    cells = []
    for cell in section.cells:
        cells.append(
            f'<article class="gui2-card gui2-tone-{attr(cell.tone)}">'
            f'<div class="gui2-label">{h(section.x_axis)}: {h(cell.x)}</div>'
            f'<div class="gui2-label">{h(section.y_axis)}: {h(cell.y)}</div>'
            f'<div class="gui2-value">{h(cell.label)}</div>'
            "</article>"
        )
    return _section_heading(section.title) + f'<div class="gui2-grid gui2-summary-grid">{"".join(cells)}</div>'


def render_timeline(section: TimelineSection) -> str:
    items = []
    for event in section.events:
        date = event.date or event.status
        body = f'<p class="gui2-muted">{h(event.body)}</p>' if event.body else ""
        items.append(
            "<li>"
            f'<div class="gui2-status">{h(date)}</div>'
            f"<div><strong>{h(event.label)}</strong>{body}</div>"
            "</li>"
        )
    return _section_heading(section.title) + f'<ol class="gui2-timeline">{"".join(items)}</ol>'


def render_flow(section: FlowSection) -> str:
    nodes = []
    labels = {node.id: node.label for node in section.nodes}
    for node in section.nodes:
        nodes.append(
            '<article class="gui2-card">'
            f"<h3>{h(node.label)}</h3>{_paragraphs(node.description or '')}"
            "</article>"
        )
    edges = []
    for edge in section.edges:
        edge_label = f" ({h(edge.label)})" if edge.label else ""
        edges.append(f"<li>{h(labels.get(edge.from_, edge.from_))} -> {h(labels.get(edge.to, edge.to))}{edge_label}</li>")
    edge_html = f'<ul class="gui2-list">{"".join(edges)}</ul>' if edges else ""
    return _section_heading(section.title) + f'<div class="gui2-flow-nodes">{"".join(nodes)}</div>{edge_html}'


def render_code(section: CodeSection) -> str:
    lines = section.code.splitlines() or [""]
    rendered_lines = [
        f'<span class="gui2-code-line" data-line="{line_no}">{h(line)}</span>'
        for line_no, line in enumerate(lines, start=1)
    ]
    annotations = _render_annotations(
        [
            {"line": note.line, "severity": note.severity, "comment": note.comment}
            for note in section.annotations
        ]
    )
    language = f'<span class="gui2-badge">{h(section.language)}</span>' if section.language else ""
    return (
        _section_heading(section.title)
        + language
        + f'<pre class="gui2-code"><code>{"".join(rendered_lines)}</code></pre>'
        + annotations
    )


def render_diff_review(section: DiffReviewSection) -> str:
    files = []
    for file in section.files:
        hunks = []
        for hunk in file.hunks:
            header = f'<div class="gui2-label">{h(hunk.header)}</div>' if hunk.header else ""
            rows = []
            for line in hunk.lines:
                prefix = {"context": " ", "add": "+", "remove": "-"}[line.type]
                line_no = line.new_line if line.type == "add" else line.old_line
                rows.append(
                    f'<tr class="gui2-diff-line-{attr(line.type)}">'
                    f'<td class="gui2-diff-prefix">{h(prefix)}</td>'
                    f"<td>{h(line_no or '')}</td>"
                    f"<td><code>{h(line.text)}</code></td>"
                    "</tr>"
                )
            hunks.append(
                f'{header}<div class="gui2-table-wrap"><table><tbody>{"".join(rows)}</tbody></table></div>'
            )
        annotations = _render_annotations(
            [
                {"line": note.line, "severity": note.severity, "comment": note.comment}
                for note in file.annotations
            ]
        )
        files.append(
            '<article class="gui2-card">'
            f"<h3>{h(file.path)}</h3>{''.join(hunks)}{annotations}"
            "</article>"
        )
    return _section_heading(section.title) + f'<div class="gui2-grid">{"".join(files)}</div>'


def render_variant_grid(section: VariantGridSection, options: RenderOptions) -> str:
    cards = []
    for variant in section.variants:
        marker = '<span class="gui2-badge">selected</span>' if variant.selected else ""
        strengths = "".join(f"<li>{h(item)}</li>" for item in variant.strengths)
        weaknesses = "".join(f"<li>{h(item)}</li>" for item in variant.weaknesses)
        preview = ""
        if variant.html_preview:
            if options.allow_trusted_html_preview:
                preview = f'<div class="gui2-preview">{variant.html_preview}</div>'
            else:
                preview = f'<pre class="gui2-preview">{h(variant.html_preview)}</pre>'
        cards.append(
            '<article class="gui2-card">'
            f"<h3>{h(variant.name)} {marker}</h3>"
            f"{_paragraphs(variant.description)}"
            f'<div class="gui2-label">Strengths</div><ul class="gui2-list">{strengths}</ul>'
            f'<div class="gui2-label">Weaknesses</div><ul class="gui2-list">{weaknesses}</ul>'
            f"{preview}</article>"
        )
    return _section_heading(section.title) + f'<div class="gui2-variants">{"".join(cards)}</div>'


def render_editable_table(section: EditableTableSection) -> str:
    header = "".join(f"<th>{h(column.label)}</th>" for column in section.columns)
    rows = []
    for row in section.rows:
        cells = []
        for column in section.columns:
            value = row.get(column.key)
            if column.input == "select":
                options = "".join(
                    f'<option value="{attr(option)}"{" selected" if option == value else ""}>{h(option)}</option>'
                    for option in column.options
                )
                control = f'<select class="gui2-form-input" data-key="{attr(column.key)}">{options}</select>'
            elif column.input == "checkbox":
                control = (
                    f'<input class="gui2-form-input" type="checkbox" data-key="{attr(column.key)}"'
                    f'{" checked" if bool(value) else ""}>'
                )
            else:
                input_type = "number" if column.input == "number" else "text"
                control = (
                    f'<input class="gui2-form-input" type="{input_type}" data-key="{attr(column.key)}"'
                    f' value="{attr(value if value is not None else "")}">'
                )
            cells.append(f"<td>{control}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return (
        _section_heading(section.title)
        + f'<div class="gui2-table-wrap"><table><thead><tr>{header}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
    )


def render_board(section: BoardSection) -> str:
    columns = []
    for column in section.columns:
        cards = []
        for card in column.cards:
            body = _paragraphs(card.body or "")
            cards.append(
                f'<article class="gui2-card gui2-tone-{attr(card.tone)}">'
                f"<h3>{h(card.title)}</h3>{body}"
                "</article>"
            )
        columns.append(
            '<section class="gui2-board-column">'
            f"<h3>{h(column.title)}</h3>{''.join(cards)}"
            "</section>"
        )
    return _section_heading(section.title) + f'<div class="gui2-board">{"".join(columns)}</div>'


def render_source_list(section: SourceListSection) -> str:
    items = []
    for source in section.sources:
        href = safe_href(source.url)
        title = f'<a href="{attr(href)}" rel="noreferrer">{h(source.title)}</a>' if href else h(source.title)
        note = f'<div class="gui2-muted">{h(source.note)}</div>' if source.note else ""
        items.append(f"<li>{title}{note}</li>")
    return _section_heading(section.title or "Sources") + f'<ol class="gui2-sources">{"".join(items)}</ol>'


def render_actions(actions: list[Any], options: RenderOptions) -> str:
    if not actions:
        return ""
    buttons = []
    for action in actions:
        if action.kind == "copy_as_json":
            buttons.append(
                f'<button class="gui2-button" data-gui2-action="copy-json">{h(action.label)}</button>'
            )
        elif action.kind == "copy_as_markdown":
            payload = json.dumps(action.template or "", ensure_ascii=False)
            buttons.append(
                f'<button class="gui2-button" data-gui2-action="copy-markdown" data-gui2-payload="{attr(payload)}">{h(action.label)}</button>'
            )
        elif action.kind == "copy_as_prompt":
            payload = json.dumps(action.payload, ensure_ascii=False)
            buttons.append(
                f'<button class="gui2-button" data-gui2-action="copy-prompt" data-gui2-payload="{attr(payload)}">{h(action.label)}</button>'
            )
        elif action.kind == "emit_intent":
            payload = json.dumps(
                {"intent": action.intent, "payload": action.payload or {}},
                ensure_ascii=False,
                sort_keys=True,
            )
            buttons.append(
                f'<button class="gui2-button secondary" data-gui2-action="emit-intent" data-gui2-payload="{attr(payload)}">{h(action.label)}</button>'
            )
    disabled_note = (
        '<span class="gui2-muted">Actions need local interactivity.</span>'
        if options.interactivity == "none"
        else ""
    )
    return f'<nav class="gui2-actions" aria-label="Artifact actions">{"".join(buttons)}{disabled_note}</nav>'


def _table(columns: Any, rows: list[dict[str, Any]]) -> str:
    header = "".join(f"<th>{h(column.label)}</th>" for column in columns)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{h(row.get(column.key, ''))}</td>" for column in columns)
        body_rows.append(f"<tr>{cells}</tr>")
    if not body_rows:
        body_rows.append(f'<tr><td colspan="{len(columns)}" class="gui2-muted">No rows</td></tr>')
    return f'<div class="gui2-table-wrap"><table><thead><tr>{header}</tr></thead><tbody>{"".join(body_rows)}</tbody></table></div>'


def _paragraphs(text: str) -> str:
    if not text:
        return ""
    paragraphs = []
    for part in text.split("\n\n"):
        lines = [h(line) for line in part.splitlines()]
        paragraphs.append(f"<p>{'<br>'.join(lines)}</p>")
    return "".join(paragraphs)


def _render_annotations(notes: list[dict[str, Any]]) -> str:
    if not notes:
        return ""
    items = []
    for note in notes:
        prefix = f"Line {note['line']}: " if note.get("line") else ""
        items.append(
            f'<li class="gui2-tone-{attr(note["severity"])}">{h(prefix)}{h(note["comment"])}</li>'
        )
    return f'<ul class="gui2-list">{"".join(items)}</ul>'
