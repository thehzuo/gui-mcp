from __future__ import annotations

from gui2_artifact_mcp.schema.artifact import Density, Theme


def render_css(theme: Theme = "neutral", density: Density = "normal") -> str:
    density_scale = {
        "compact": ("12px", "14px", "8px"),
        "normal": ("16px", "16px", "12px"),
        "presentation": ("22px", "18px", "16px"),
    }[density]
    theme_tokens = {
        "neutral": ("#ffffff", "#f7f7f5", "#151515", "#666666"),
        "technical": ("#fbfcfd", "#f3f6f8", "#111827", "#52606d"),
        "warm": ("#fffdf8", "#f8f2e8", "#1f1b16", "#6f6353"),
        "mono": ("#ffffff", "#f4f4f4", "#101010", "#5f5f5f"),
    }[theme]
    gap, font_size, radius = density_scale
    bg, surface, text, muted = theme_tokens
    return f"""
:root {{
  --gui2-bg: {bg};
  --gui2-surface: {surface};
  --gui2-elevated: #ffffff;
  --gui2-border: #dedede;
  --gui2-text: {text};
  --gui2-muted: {muted};
  --gui2-good: #176b3a;
  --gui2-warning: #8a5a00;
  --gui2-danger: #9b1c1c;
  --gui2-info: #155e75;
  --gui2-radius: {radius};
  --gui2-gap: {gap};
  --gui2-font-size: {font_size};
  --gui2-code-bg: #111827;
  --gui2-code-text: #f9fafb;
}}
* {{ box-sizing: border-box; }}
html {{ background: var(--gui2-bg); color: var(--gui2-text); }}
body {{
  margin: 0;
  font: 400 var(--gui2-font-size)/1.5 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
  letter-spacing: 0;
}}
a {{ color: var(--gui2-info); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
.gui2-shell {{ max-width: 1120px; margin: 0 auto; padding: clamp(16px, 4vw, 48px); }}
.gui2-header {{ margin-bottom: calc(var(--gui2-gap) * 1.5); }}
.gui2-kicker {{
  display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 10px;
  color: var(--gui2-muted); font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em;
}}
.gui2-header h1 {{ margin: 0; font-size: clamp(2rem, 5vw, 4rem); line-height: 1.02; letter-spacing: 0; }}
.gui2-subtitle {{ margin: 12px 0 0; max-width: 72ch; color: var(--gui2-muted); font-size: 1.05rem; }}
.gui2-section {{
  padding: calc(var(--gui2-gap) * 1.1) 0;
  border-top: 1px solid var(--gui2-border);
}}
.gui2-section h2 {{ margin: 0 0 12px; font-size: 1.15rem; line-height: 1.2; letter-spacing: 0; }}
.gui2-section h3 {{ margin: 0 0 8px; font-size: 1rem; line-height: 1.25; letter-spacing: 0; }}
.gui2-grid {{ display: grid; gap: var(--gui2-gap); }}
.gui2-summary-grid {{ grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }}
.gui2-card, .gui2-callout, .gui2-board-column {{
  background: var(--gui2-surface);
  border: 1px solid var(--gui2-border);
  border-radius: var(--gui2-radius);
  padding: var(--gui2-gap);
}}
.gui2-label {{ color: var(--gui2-muted); font-size: 0.82rem; margin-bottom: 4px; }}
.gui2-value {{ font-weight: 650; }}
.gui2-tone-good {{ border-color: color-mix(in srgb, var(--gui2-good), var(--gui2-border) 65%); }}
.gui2-tone-warning {{ border-color: color-mix(in srgb, var(--gui2-warning), var(--gui2-border) 65%); }}
.gui2-tone-danger {{ border-color: color-mix(in srgb, var(--gui2-danger), var(--gui2-border) 65%); }}
.gui2-tone-info {{ border-color: color-mix(in srgb, var(--gui2-info), var(--gui2-border) 65%); }}
.gui2-badge {{
  display: inline-flex; align-items: center; min-height: 24px; padding: 2px 8px;
  border: 1px solid var(--gui2-border); border-radius: 999px; background: var(--gui2-surface);
  color: var(--gui2-muted); font-size: 0.78rem;
}}
.gui2-table-wrap {{ overflow-x: auto; border: 1px solid var(--gui2-border); border-radius: var(--gui2-radius); }}
table {{ width: 100%; border-collapse: collapse; min-width: 520px; background: var(--gui2-elevated); }}
th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--gui2-border); text-align: left; vertical-align: top; }}
th {{ background: var(--gui2-surface); font-size: 0.84rem; color: var(--gui2-muted); }}
tr:last-child td {{ border-bottom: 0; }}
.gui2-list {{ margin: 0; padding-left: 1.2rem; }}
.gui2-list li + li {{ margin-top: 8px; }}
.gui2-checklist {{ list-style: none; padding-left: 0; }}
.gui2-checklist li {{ display: flex; gap: 10px; align-items: flex-start; padding: 8px 0; }}
.gui2-priority {{ margin-left: auto; color: var(--gui2-muted); font-size: 0.82rem; }}
.gui2-timeline {{ list-style: none; padding-left: 0; margin: 0; }}
.gui2-timeline li {{ display: grid; grid-template-columns: 120px 1fr; gap: var(--gui2-gap); padding: 10px 0; }}
.gui2-status {{ color: var(--gui2-muted); font-size: 0.84rem; }}
.gui2-flow-nodes, .gui2-variants, .gui2-comparison, .gui2-board {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--gui2-gap);
}}
.gui2-code {{
  overflow-x: auto; margin: 0; padding: var(--gui2-gap); border-radius: var(--gui2-radius);
  background: var(--gui2-code-bg); color: var(--gui2-code-text); font-size: 0.9rem;
}}
.gui2-code code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
.gui2-code-line {{ display: block; min-height: 1.4em; white-space: pre; }}
.gui2-code-line::before {{
  content: attr(data-line); display: inline-block; width: 3.5ch; margin-right: 12px; color: #9ca3af;
}}
.gui2-diff-line-add {{ background: #e9f7ee; }}
.gui2-diff-line-remove {{ background: #fdecec; }}
.gui2-diff-prefix {{ width: 3ch; color: var(--gui2-muted); }}
.gui2-preview {{
  white-space: pre-wrap; overflow-x: auto; padding: 12px; border-radius: calc(var(--gui2-radius) / 1.5);
  border: 1px solid var(--gui2-border); background: #fff; color: var(--gui2-muted);
}}
.gui2-form-input {{
  width: 100%; min-width: 120px; padding: 7px 8px; border: 1px solid var(--gui2-border);
  border-radius: 6px; background: #fff; color: var(--gui2-text); font: inherit;
}}
.gui2-actions {{ display: flex; flex-wrap: wrap; gap: 10px; padding-top: var(--gui2-gap); }}
.gui2-button {{
  border: 1px solid var(--gui2-border); border-radius: 8px; background: var(--gui2-text); color: #fff;
  padding: 8px 12px; font: inherit; cursor: pointer;
}}
.gui2-button.secondary {{ background: var(--gui2-surface); color: var(--gui2-text); }}
.gui2-sources {{ padding-left: 1.2rem; }}
.gui2-muted {{ color: var(--gui2-muted); }}
@media (max-width: 680px) {{
  .gui2-shell {{ padding: 18px; }}
  .gui2-timeline li {{ grid-template-columns: 1fr; gap: 2px; }}
  table {{ min-width: 480px; }}
}}
@media print {{
  body {{ background: #fff; }}
  .gui2-shell {{ max-width: none; padding: 0; }}
  .gui2-actions {{ display: none; }}
  .gui2-section {{ break-inside: avoid; }}
}}
""".strip()
