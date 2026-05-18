from __future__ import annotations

import json
from pathlib import Path

from gui2_artifact_mcp.render.artifact import render_artifact_to_html
from gui2_artifact_mcp.schema.artifact import ArtifactSpec
from gui2_artifact_mcp.util.escape import h

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "demo" / "index.html"


def main() -> int:
    output = DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    examples = sorted((ROOT / "examples").rglob("*.json"))
    cards = []
    for path in examples:
        spec = ArtifactSpec.model_validate(json.loads(path.read_text(encoding="utf-8")))
        rendered = render_artifact_to_html(spec)
        rel = path.relative_to(ROOT)
        slug = path.stem.replace("_", "-")
        demo_path = output.parent / f"{slug}.html"
        demo_path.write_text(rendered.html, encoding="utf-8")
        cards.append(
            f"""
            <article class="demo-card" data-version="{h(spec.v)}">
              <div class="demo-meta">
                <span>{h(spec.v)}</span>
                <span>{h(spec.artifact.replace("_", " "))}</span>
              </div>
              <h2>{h(spec.title)}</h2>
              <p>{h(spec.subtitle or str(rel))}</p>
              <iframe title="{h(spec.title)} preview" src="{h(demo_path.name)}" loading="lazy"></iframe>
              <div class="demo-actions">
                <a href="{h(demo_path.name)}" target="_blank" rel="noreferrer">Open full page</a>
                <code>{h(str(rel))}</code>
              </div>
            </article>
            """
        )
    output.write_text(_gallery_html("".join(cards), len(examples)), encoding="utf-8")
    print(f"Wrote {output} with {len(examples)} artifacts")
    return 0


def _gallery_html(cards: str, count: int) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GUI2 Artifact Demo Gallery</title>
  <style>
    :root {{
      --paper: #fbf7ed;
      --sheet: #fffdf6;
      --ink: #171512;
      --muted: #6c6255;
      --line: #27231d;
      --accent: #c43d2b;
      --blue: #2458a6;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        linear-gradient(rgba(39,35,29,.055) 1px, transparent 1px),
        linear-gradient(90deg, rgba(39,35,29,.045) 1px, transparent 1px),
        var(--paper);
      background-size: 28px 28px;
      font: 15px/1.5 "Avenir Next", "Gill Sans", "Trebuchet MS", sans-serif;
    }}
    header {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 54px 24px 28px;
      border-bottom: 2px solid var(--line);
    }}
    .eyebrow {{
      display: flex;
      gap: 10px;
      align-items: center;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .12em;
    }}
    .eyebrow::before {{
      content: "";
      width: 32px;
      height: 2px;
      background: var(--accent);
    }}
    h1 {{
      max-width: 12ch;
      margin: 14px 0 0;
      font: 500 clamp(3rem, 8vw, 7rem)/.9 "Iowan Old Style", "Palatino Linotype", Georgia, serif;
      letter-spacing: 0;
    }}
    .intro {{
      max-width: 760px;
      margin: 18px 0 0;
      color: var(--muted);
      font-size: 17px;
    }}
    main {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px;
      display: grid;
      gap: 24px;
      grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
    }}
    .demo-card {{
      display: grid;
      gap: 12px;
      min-width: 0;
      padding: 16px;
      border: 2px solid var(--line);
      border-radius: 10px;
      background: var(--sheet);
      box-shadow: 8px 8px 0 rgba(39,35,29,.11);
    }}
    .demo-card[data-version="0.2"] {{
      box-shadow: 8px 8px 0 rgba(196,61,43,.18);
    }}
    .demo-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .demo-meta span {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 2px 8px;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .06em;
    }}
    h2 {{
      margin: 0;
      font: 600 24px/1.05 "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    }}
    p {{ margin: 0; color: var(--muted); }}
    iframe {{
      width: 100%;
      height: 520px;
      border: 1.5px solid var(--line);
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
    a {{
      color: white;
      background: var(--ink);
      border: 1.5px solid var(--line);
      border-radius: 7px;
      padding: 8px 12px;
      text-decoration: none;
    }}
    code {{
      color: var(--blue);
      font-size: 12px;
    }}
    @media (max-width: 560px) {{
      main {{ grid-template-columns: 1fr; padding: 14px; }}
      iframe {{ height: 460px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="eyebrow">GUI2 artifact MCP demo gallery</div>
    <h1>All generated artifacts</h1>
    <p class="intro">{count} bundled examples rendered as deterministic HTML. Each card embeds a preview and links to the full generated page for Chrome verification.</p>
  </header>
  <main>
    {cards}
  </main>
</body>
</html>"""


if __name__ == "__main__":
    raise SystemExit(main())
