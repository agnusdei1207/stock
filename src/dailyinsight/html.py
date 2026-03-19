from __future__ import annotations

from html import escape
from pathlib import Path

from .models import AgentOutput, DailyInsight


def _table(rows: list[dict[str, str]], columns: list[str]) -> str:
    if not rows:
        return "<p>No data.</p>"
    head = "".join(f"<th>{escape(col)}</th>" for col in columns)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{escape(str(row.get(col, '')))}</td>" for col in columns)
        body_rows.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def _list(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def _agent_cards(agent_outputs: dict[str, AgentOutput]) -> str:
    cards = []
    for key in (
        "source_gate",
        "emerging_scout",
        "scout",
        "macro",
        "domain",
        "fraud_guard",
        "bull",
        "bear",
        "reflection",
        "strategy",
        "report_verifier",
    ):
        if key not in agent_outputs:
            continue
        cards.append(
            f"<div class='card'><h3>{escape(key)}</h3><p>{escape(agent_outputs[key].summary)}</p></div>"
        )
    return "<div class='grid'>" + "".join(cards) + "</div>"


def render_html(insight: DailyInsight, agent_outputs: dict[str, AgentOutput]) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(insight.title)}</title>
  <style>
    :root {{
      --bg: #f5f1e8;
      --paper: #fffdf8;
      --ink: #10212b;
      --muted: #52606b;
      --line: #d8d0c0;
      --accent: #b44f25;
      --accent-soft: #f1dfd4;
      --ok: #215732;
      --warn: #8b5a00;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Iowan Old Style", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #f3e7cf 0, transparent 30%),
        linear-gradient(180deg, #f7f3eb 0%, #efe7da 100%);
    }}
    .page {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 48px 24px 96px;
    }}
    header {{
      background: var(--paper);
      border: 1px solid var(--line);
      padding: 28px;
      border-radius: 24px;
      box-shadow: 0 12px 30px rgba(16, 33, 43, 0.08);
    }}
    h1, h2, h3 {{ margin: 0 0 12px; line-height: 1.15; }}
    h1 {{ font-size: 2.3rem; max-width: 14ch; }}
    h2 {{ font-size: 1.35rem; margin-top: 36px; }}
    h3 {{ font-size: 1rem; color: var(--accent); }}
    p, li {{ line-height: 1.6; }}
    .lede {{ color: var(--muted); max-width: 70ch; }}
    .pill {{
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 0.82rem;
      margin-right: 8px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
    }}
    .card {{
      background: var(--paper);
      border: 1px solid var(--line);
      padding: 18px;
      border-radius: 18px;
    }}
    .section {{
      margin-top: 24px;
      background: var(--paper);
      border: 1px solid var(--line);
      padding: 24px;
      border-radius: 24px;
      box-shadow: 0 8px 24px rgba(16, 33, 43, 0.05);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
      overflow: hidden;
    }}
    th, td {{
      text-align: left;
      vertical-align: top;
      border-bottom: 1px solid var(--line);
      padding: 10px 12px;
    }}
    th {{
      color: var(--accent);
      background: #fbf5ec;
    }}
    pre {{
      background: #181c20;
      color: #f8f7f4;
      padding: 16px;
      border-radius: 16px;
      overflow-x: auto;
      font-size: 0.9rem;
    }}
    a {{ color: var(--accent); }}
  </style>
</head>
<body>
  <main class="page">
    <header>
      <div>
        <span class="pill">{escape(insight.date)}</span>
        <span class="pill">{escape(insight.selected_asset.get("ticker", ""))}</span>
        <span class="pill">Confidence {escape(str(insight.confidence))}</span>
        <span class="pill">Risk {escape(str(insight.risk_level))}</span>
      </div>
      <h1>{escape(insight.title)}</h1>
      <p class="lede">{escape(insight.subtitle)}</p>
      {_list(insight.executive_summary)}
    </header>

    <section class="section">
      <h2>Decision Dashboard</h2>
      {_table(insight.dashboard, ["item", "conclusion", "reason"])}
    </section>

    <section class="section">
      <h2>Source Validation</h2>
      {_table(insight.source_table, ["source", "grade", "status", "reason", "url"])}
    </section>

    <section class="section">
      <h2>World Market and Scouting</h2>
      {_table(insight.macro_table, ["axis", "view", "impact"])}
      <br />
      {_table(insight.scouting_table, ["candidate", "ticker", "theme", "why_now", "status"])}
      <br />
      {_table(insight.emerging_table, ["candidate", "stage", "quality_view", "value_view", "reason"])}
    </section>

    <section class="section">
      <h2>Price and Scenario</h2>
      {_table(insight.price_table, ["type", "price", "date", "vs_current", "comment"])}
      <br />
      {_table(insight.range_table, ["period", "low", "high", "position", "comment"])}
      <br />
      {_table(insight.scenario_table, ["scenario", "target", "upside", "probability", "trigger"])}
    </section>

    <section class="section">
      <h2>Domain, Competition, and Risks</h2>
      {_table(insight.domain_table, ["item", "conclusion", "reason"])}
      <br />
      {_table(insight.competition_table, ["company", "strength", "weakness", "view"])}
      <br />
      {_table(insight.fraud_table, ["check", "status", "reason"])}
      <br />
      {_table(insight.risk_table, ["risk", "level", "reason", "response"])}
    </section>

    <section class="section">
      <h2>Debate and Verification</h2>
      {_table(insight.debate_table, ["point", "bull", "bear", "decision"])}
      <br />
      {_table(insight.verification_table, ["check", "status", "note"])}
      <br />
      {_table(insight.final_review_table, ["check", "status", "note"])}
    </section>

    <section class="section">
      <h2>Probabilities and Future View</h2>
      {_table(insight.probability_table, ["outcome", "probability", "reason"])}
      <br />
      {_table(insight.future_view_table, ["horizon", "view", "reason"])}
    </section>

    <section class="section">
      <h2>Execution</h2>
      {_table(insight.buy_plan, ["step", "condition", "size", "reason"])}
      <br />
      {_table(insight.sell_plan, ["step", "condition", "size", "reason"])}
      <p><strong>Final action:</strong> {escape(insight.action)}</p>
      <h3>Catalysts</h3>
      {_list(insight.catalysts)}
      <h3>Watch Items</h3>
      {_list(insight.watch_items)}
    </section>

    <section class="section">
      <h2>Evidence and News</h2>
      {_table(insight.evidence_table, ["claim", "evidence"])}
      <br />
      {_table(insight.news_table, ["headline", "source", "quality", "impact", "judgment", "url"])}
      <h3>Rejected Alternatives</h3>
      {_list(insight.rejected_alternatives)}
    </section>

    <section class="section">
      <h2>Agent Trace</h2>
      {_agent_cards(agent_outputs)}
    </section>
  </main>
</body>
</html>
"""


def write_html_report(output_dir: str, insight: DailyInsight, content: str) -> str:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    target = path / f"{insight.date}_daily_master_report.html"
    target.write_text(content, encoding="utf-8")
    return str(target)


def write_site_index(output_dir: str, reports: list[tuple[str, str]]) -> str:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    items = "".join(
        f"<li><a href='{escape(link)}'>{escape(label)}</a></li>"
        for label, link in sorted(reports, reverse=True)
    )
    content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>stock daily reports</title>
  <style>
    body {{ font-family: Georgia, serif; margin: 0; background: #f5f1e8; color: #10212b; }}
    main {{ max-width: 900px; margin: 0 auto; padding: 48px 24px; }}
    .wrap {{ background: #fffdf8; border: 1px solid #d8d0c0; border-radius: 24px; padding: 28px; }}
    a {{ color: #b44f25; }}
  </style>
</head>
<body>
  <main>
    <div class="wrap">
      <h1>stock daily reports</h1>
      <p>Static HTML output for GitHub Pages.</p>
      <ul>{items}</ul>
    </div>
  </main>
</body>
</html>
"""
    target = path / "index.html"
    target.write_text(content, encoding="utf-8")
    return str(target)
