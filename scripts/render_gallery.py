from __future__ import annotations

import json
from pathlib import Path

from gui2_artifact_mcp.render.artifact import render_artifact_to_html
from gui2_artifact_mcp.schema.artifact import ArtifactSpec
from gui2_artifact_mcp.util.escape import attr, h

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "demo" / "index.html"


def main() -> int:
    output = DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    for stale_page in output.parent.glob("*.html"):
        if stale_page != output:
            stale_page.unlink()

    examples = sorted((ROOT / "examples").rglob("*.json"))
    sandbox_section_kinds = {
        "prototype_flow",
        "animation_controls",
        "dependency_toggle_list",
        "prompt_tuner",
    }
    interactive_section_kinds = {
        "tabs",
        "filterable_collection",
        "inspector_diagram",
        "board",
        "slide_deck",
        "token_sheet",
        "copyable_asset_grid",
    }

    cards: list[str] = []
    nav_items: list[str] = []
    for path in examples:
        spec = ArtifactSpec.model_validate(json.loads(path.read_text(encoding="utf-8")))
        rendered = render_artifact_to_html(spec)
        rel = path.relative_to(ROOT)
        slug = "-".join(path.relative_to(ROOT / "examples").with_suffix("").parts).replace("_", "-")
        demo_path = output.parent / f"{slug}.html"
        demo_path.write_text(rendered.html, encoding="utf-8")

        card_id = f"artifact-{slug}"
        section_kinds = [section.kind for section in spec.sections]
        unique_section_kinds = list(dict.fromkeys(section_kinds))
        has_sandbox = any(kind in sandbox_section_kinds for kind in section_kinds)
        has_interactions = bool(spec.interactions) or has_sandbox or any(
            kind in interactive_section_kinds for kind in section_kinds
        )
        tags = [
            "all",
            f"v{spec.v.replace('.', '')}",
            spec.artifact,
            *unique_section_kinds,
            "sandbox" if has_sandbox else "",
            "interactive" if has_interactions else "",
        ]
        tag_attr = " ".join(tag for tag in tags if tag)
        section_summary = ", ".join(kind.replace("_", " ") for kind in unique_section_kinds[:4])
        if len(unique_section_kinds) > 4:
            section_summary += f" +{len(unique_section_kinds) - 4}"
        interaction_summary = "interactive" if has_interactions else "static"

        nav_items.append(
            f'<li><a href="#{attr(card_id)}"><span>{h(spec.v)}</span>{h(spec.title)}</a></li>'
        )
        cards.append(
            f"""
            <article class="demo-card" id="{attr(card_id)}" data-version="{h(spec.v)}" data-filter-tags="{attr(tag_attr)}">
              <div class="demo-card-header">
                <div>
                  <div class="demo-meta">
                    <span>{h(spec.v)}</span>
                    <span>{h(spec.artifact.replace("_", " "))}</span>
                    <span>{h(str(rel.parent))}</span>
                  </div>
                  <h2>{h(spec.title)}</h2>
                  <p>{h(spec.subtitle or str(rel))}</p>
                </div>
                <a class="demo-open" href="{h(demo_path.name)}" target="_blank" rel="noreferrer">Open full page</a>
              </div>
              <dl class="demo-stats">
                <div><dt>Sections</dt><dd>{len(section_kinds)}</dd></div>
                <div><dt>Mode</dt><dd>{h(interaction_summary)}</dd></div>
                <div><dt>Uses</dt><dd>{h(section_summary or "sections")}</dd></div>
              </dl>
              <iframe title="{h(spec.title)} preview" src="{h(demo_path.name)}" loading="lazy"></iframe>
              <div class="demo-actions">
                <code>{h(str(rel))}</code>
              </div>
            </article>
            """
        )

    output.write_text(_gallery_html("".join(cards), "".join(nav_items), len(examples)), encoding="utf-8")
    print(f"Wrote {output} with {len(examples)} artifacts")
    return 0


def _gallery_html(cards: str, nav_items: str, count: int) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GUI2 Artifact Demo Gallery</title>
  <style>
    :root {{
      --page: #f5f5f7;
      --sheet: #ffffff;
      --ink: #1d1d1f;
      --muted: #6e6e73;
      --line: #d2d2d7;
      --accent: #0071e3;
      --blue: #0066cc;
      --shadow: 0 1px 2px rgba(0,0,0,.04), 0 12px 28px rgba(0,0,0,.06);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--page);
      font: 16px/1.58 -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif;
    }}
    header {{
      max-width: 1520px;
      margin: 0 auto;
      padding: 28px 24px 22px;
      display: grid;
      align-content: start;
      justify-items: start;
      text-align: left;
      border-bottom: 1px solid var(--line);
    }}
    .eyebrow {{
      display: flex;
      gap: 10px;
      align-items: center;
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0;
    }}
    .eyebrow::before {{
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent);
    }}
    h1 {{
      max-width: 18ch;
      margin: 10px 0 0;
      font: 700 clamp(2.1rem, 4.6vw, 4.2rem)/1.04 -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif;
      letter-spacing: 0;
    }}
    .intro {{
      max-width: 820px;
      margin: 10px 0 0;
      color: var(--muted);
      font-size: clamp(1rem, 1.4vw, 1.18rem);
      line-height: 1.5;
    }}
    .demo-layout {{
      max-width: 1520px;
      margin: 0 auto;
      padding: 24px;
      display: grid;
      gap: 24px;
      grid-template-columns: minmax(220px, 270px) minmax(0, 1fr);
      align-items: start;
    }}
    .demo-index {{
      position: sticky;
      top: 18px;
      max-height: calc(100vh - 36px);
      overflow: auto;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,.82);
      box-shadow: var(--shadow);
      backdrop-filter: saturate(180%) blur(20px);
    }}
    .demo-index h2 {{
      margin: 0 0 10px;
      font: 700 17px/1.2 -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif;
    }}
    .demo-filter-group {{
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      margin: 0 0 14px;
      padding-bottom: 14px;
      border-bottom: 1px solid var(--line);
    }}
    .demo-filter {{
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--ink);
      padding: 6px 10px;
      font: inherit;
      font-size: 13px;
      cursor: pointer;
    }}
    .demo-filter[aria-pressed="true"] {{
      background: var(--ink);
      border-color: var(--ink);
      color: #fff;
    }}
    .demo-index ol {{
      display: grid;
      gap: 4px;
      margin: 0;
      padding: 0;
      list-style: none;
    }}
    .demo-index a {{
      display: grid;
      gap: 2px;
      padding: 7px 8px;
      color: var(--ink);
      background: transparent;
      border: 0;
      border-radius: 8px;
      text-decoration: none;
    }}
    .demo-index a:hover {{ background: #f5f5f7; }}
    .demo-index span {{
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .08em;
    }}
    .demo-list {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(440px, 1fr));
      gap: 20px;
    }}
    .demo-card {{
      display: grid;
      gap: 14px;
      min-width: 0;
      scroll-margin-top: 18px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--sheet);
      box-shadow: var(--shadow);
    }}
    .demo-card[data-version="0.2"] {{
      border-color: color-mix(in srgb, var(--accent), var(--line) 72%);
    }}
    .demo-card-header {{
      display: grid;
      gap: 12px;
      align-items: start;
    }}
    .demo-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .demo-meta span {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 3px 9px;
      background: #fbfbfd;
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0;
      font: 700 clamp(1.28rem, 2vw, 1.75rem)/1.12 -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif;
    }}
    p {{ margin: 8px 0 0; max-width: 82ch; color: var(--muted); line-height: 1.66; }}
    .demo-stats {{
      display: grid;
      grid-template-columns: 80px 100px minmax(0, 1fr);
      gap: 8px;
      margin: 0;
    }}
    .demo-stats div {{
      min-width: 0;
      padding: 9px 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfbfd;
    }}
    .demo-stats dt {{
      color: var(--muted);
      font-size: 11px;
    }}
    .demo-stats dd {{
      margin: 2px 0 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 13px;
      font-weight: 650;
    }}
    iframe {{
      width: 100%;
      height: 360px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
    }}
    .demo-actions {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .demo-open {{
      justify-self: start;
      color: white;
      background: var(--accent);
      border: 1px solid var(--accent);
      border-radius: 999px;
      padding: 8px 15px;
      text-decoration: none;
      white-space: nowrap;
    }}
    .demo-open:hover {{ background: #147ce5; }}
    code {{
      color: var(--blue);
      font-size: 12px;
    }}
    @media (max-width: 960px) {{
      .demo-layout {{ grid-template-columns: 1fr; }}
      .demo-index {{ position: static; max-height: none; }}
      .demo-index ol {{ grid-template-columns: 1fr; }}
      .demo-list {{ grid-template-columns: 1fr; }}
      .demo-card-header {{ grid-template-columns: 1fr; }}
      .demo-open {{ justify-self: start; }}
    }}
    @media (max-width: 560px) {{
      header {{ padding: 28px 14px 22px; }}
      .demo-layout {{ padding: 14px; }}
      .demo-stats {{ grid-template-columns: 1fr; }}
      iframe {{ height: 320px; }}
    }}
    .demo-card[hidden] {{ display: none; }}
  </style>
</head>
<body>
  <header>
    <div class="eyebrow">GUI2 artifact MCP demo gallery</div>
    <h1>All generated artifacts</h1>
    <p class="intro">{count} bundled examples rendered as deterministic HTML. Each card embeds a compact preview and links to the full generated page for Chrome verification.</p>
  </header>
  <main class="demo-layout">
    <aside class="demo-index" aria-label="Artifact index">
      <h2>Review index</h2>
      <div class="demo-filter-group" aria-label="Gallery filters">
        <button class="demo-filter" type="button" data-demo-filter="all" aria-pressed="true">All</button>
        <button class="demo-filter" type="button" data-demo-filter="v01" aria-pressed="false">v0.1</button>
        <button class="demo-filter" type="button" data-demo-filter="v02" aria-pressed="false">v0.2</button>
        <button class="demo-filter" type="button" data-demo-filter="interactive" aria-pressed="false">Interactive</button>
        <button class="demo-filter" type="button" data-demo-filter="sandbox" aria-pressed="false">Sandbox</button>
      </div>
      <ol>{nav_items}</ol>
    </aside>
    <div class="demo-list">
      {cards}
    </div>
  </main>
  <script>
    (() => {{
      const controls = [...document.querySelectorAll("[data-demo-filter]")];
      const cards = [...document.querySelectorAll(".demo-card")];
      const applyFilter = (filter) => {{
        controls.forEach((control) => {{
          control.setAttribute("aria-pressed", String(control.dataset.demoFilter === filter));
        }});
        cards.forEach((card) => {{
          const tags = (card.dataset.filterTags || "").split(" ");
          card.hidden = filter !== "all" && !tags.includes(filter);
        }});
      }};
      document.addEventListener("click", (event) => {{
        const control = event.target.closest("[data-demo-filter]");
        if (control) applyFilter(control.dataset.demoFilter);
      }});
    }})();
  </script>
</body>
</html>"""


if __name__ == "__main__":
    raise SystemExit(main())
