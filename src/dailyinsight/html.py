from __future__ import annotations

import json
import shutil
from html import escape
from pathlib import Path

from .models import AgentOutput, DailyInsight


SITE_CSS = """
:root {
  --color-brand: 210 90% 56%;
  --color-brand-light: 210 95% 90%;
  --color-brand-dark: 210 85% 22%;
  --color-surface: 0 0% 100%;
  --color-surface-muted: 220 18% 95%;
  --color-text: 220 28% 12%;
  --color-text-secondary: 220 12% 42%;
  --color-border: 220 18% 88%;

  --bg-base: #eef4fb;
  --bg-elevated: #f7fbff;
  --bg-header: rgba(245, 250, 255, 0.88);
  --bg-card: hsl(var(--color-surface));
  --bg-muted: hsl(var(--color-surface-muted));
  --text-primary: hsl(var(--color-text));
  --text-secondary: hsl(var(--color-text-secondary));
  --text-accent: hsl(var(--color-brand));
  --border-default: hsl(var(--color-border));
  --border-accent: hsl(var(--color-brand) / 0.3);
  --highlight-bg: hsl(var(--color-brand-light));
  --highlight-text: hsl(var(--color-brand-dark));
  --shadow-sm: 0 1px 2px rgba(21, 57, 94, 0.05);
  --shadow-md: 0 8px 20px rgba(21, 57, 94, 0.08);
  --shadow-lg: 0 20px 40px rgba(21, 57, 94, 0.12);
  --radius: 18px;
  --max-width: 980px;
}

[data-theme="dark"] {
  --bg-base: #08101b;
  --bg-elevated: #0c1522;
  --bg-header: rgba(8, 16, 27, 0.88);
  --bg-card: #0f1b2b;
  --bg-muted: #132235;
  --text-primary: #f3f7fc;
  --text-secondary: #9db0c6;
  --text-accent: #6fb8ff;
  --border-default: #1e3047;
  --border-accent: rgba(111, 184, 255, 0.35);
  --highlight-bg: rgba(65, 132, 255, 0.18);
  --highlight-text: #9dcaff;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  font-size: 16px;
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: radial-gradient(circle at top left, rgba(118, 180, 255, 0.18), transparent 30%), var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
}

a {
  color: inherit;
  text-decoration: none;
}

.container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 24px;
}

.site-header {
  padding: 56px 0 28px;
}

.header-inner {
  display: flex;
  flex-direction: column;
  gap: 18px;
  align-items: center;
}

.site-logo {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.04em;
}

.site-logo span {
  color: var(--text-accent);
}

.header-search {
  position: relative;
  width: 100%;
  max-width: 680px;
}

.header-search input {
  width: 100%;
  height: 48px;
  border-radius: 14px;
  border: 1px solid transparent;
  background: var(--bg-muted);
  color: var(--text-primary);
  padding: 0 16px 0 46px;
  outline: none;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.header-search input:focus {
  border-color: var(--text-accent);
  box-shadow: 0 0 0 4px rgba(76, 148, 255, 0.13);
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
}

.hero {
  padding: 18px 0 8px;
}

.hero-card,
.section-card,
.report-shell {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: 24px;
  box-shadow: var(--shadow-md);
}

.hero-card {
  padding: 28px;
}

.hero-title {
  font-size: 2.2rem;
  line-height: 1.08;
  letter-spacing: -0.04em;
  margin: 0 0 10px;
}

.hero-copy {
  color: var(--text-secondary);
  max-width: 70ch;
  margin: 0;
}

.hero-pills,
.report-pills {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 16px;
}

.pill {
  border-radius: 999px;
  background: var(--highlight-bg);
  color: var(--highlight-text);
  padding: 6px 10px;
  font-size: 0.82rem;
  font-weight: 600;
}

.section-card {
  margin-top: 20px;
  padding: 24px;
}

.section-title {
  margin: 0 0 14px;
  font-size: 1.2rem;
  letter-spacing: -0.02em;
}

.muted {
  color: var(--text-secondary);
}

.product-grid,
.report-grid,
.agent-grid {
  display: grid;
  gap: 16px;
}

.product-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.report-grid {
  grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
}

.agent-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.product-card,
.report-card,
.agent-card {
  border: 1px solid var(--border-default);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255,255,255,0.7), transparent), var(--bg-card);
  padding: 18px;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.product-card:hover,
.report-card:hover,
.agent-card:hover {
  transform: translateY(-2px);
  border-color: var(--border-accent);
}

.product-title,
.report-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 10px 0 6px;
  letter-spacing: -0.02em;
}

.product-desc,
.report-desc,
.agent-card p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.95rem;
}

.report-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 10px;
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.report-shell {
  padding: 28px;
  margin-top: 16px;
}

.report-title-main {
  font-size: 2.35rem;
  line-height: 1.08;
  letter-spacing: -0.045em;
  margin: 12px 0;
}

.report-subtitle {
  color: var(--text-secondary);
  margin: 0 0 16px;
  max-width: 72ch;
}

.report-section {
  margin-top: 24px;
}

.report-section h2 {
  margin: 0 0 12px;
  font-size: 1.35rem;
  letter-spacing: -0.03em;
}

.report-section h3 {
  margin: 16px 0 10px;
  font-size: 1rem;
  color: var(--text-accent);
}

table {
  width: 100%;
  border-collapse: collapse;
  overflow: hidden;
  border-radius: 14px;
  font-size: 0.94rem;
}

th,
td {
  text-align: left;
  vertical-align: top;
  padding: 11px 12px;
  border-bottom: 1px solid var(--border-default);
}

th {
  background: var(--bg-muted);
  color: var(--text-accent);
}

pre {
  background: #0f1724;
  color: #eef5ff;
  border-radius: 16px;
  padding: 16px;
  overflow-x: auto;
  box-shadow: var(--shadow-sm);
}

mark {
  background: var(--highlight-bg);
  color: var(--highlight-text);
  border-radius: 4px;
  padding: 0 2px;
}

.empty {
  color: var(--text-secondary);
  text-align: center;
  padding: 14px 0 2px;
}

@media (max-width: 720px) {
  .hero-title,
  .report-title-main {
    font-size: 1.7rem;
  }
  .container {
    padding: 0 16px;
  }
  .hero-card,
  .section-card,
  .report-shell {
    padding: 18px;
    border-radius: 18px;
  }
}
"""


SITE_JS = """
(function () {
  var themeKey = 'stock-theme';
  var root = document.documentElement;
  var current = localStorage.getItem(themeKey) || 'light';
  root.setAttribute('data-theme', current);

  var themeBtn = document.getElementById('theme-btn');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem(themeKey, next);
    });
  }

  var dataEl = document.getElementById('report-data');
  var input = document.getElementById('site-search');
  var cards = Array.prototype.slice.call(document.querySelectorAll('[data-report-card]'));
  if (!input || !dataEl || cards.length === 0) return;

  var reports = [];
  try {
    reports = JSON.parse(dataEl.textContent || '[]');
  } catch (err) {
    reports = [];
  }

  function applyFilter(query) {
    var q = query.trim().toLowerCase();
    cards.forEach(function (card) {
      var hay = (card.getAttribute('data-search') || '').toLowerCase();
      card.style.display = !q || hay.indexOf(q) !== -1 ? '' : 'none';
    });
  }

  input.addEventListener('input', function () {
    applyFilter(input.value);
  });

  window.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
    }
  });
})();
"""


def _table(rows: list[dict[str, str]], columns: list[str]) -> str:
    if not rows:
        return "<p class='empty'>No data.</p>"
    head = "".join(f"<th>{escape(col)}</th>" for col in columns)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{escape(str(row.get(col, '')))}</td>" for col in columns)
        body_rows.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def _list(items: list[str]) -> str:
    if not items:
        return "<p class='empty'>No items.</p>"
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def _layout(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/stock/assets/css/style.css" />
</head>
<body>
  <header class="site-header">
    <div class="container">
      <div class="header-inner">
        <a href="/stock/" class="site-logo">Stock<span>Lab</span></a>
        <div class="header-search">
          <span class="search-icon">⌕</span>
          <input id="site-search" type="text" placeholder="Search reports, themes, tickers..." autocomplete="off" />
        </div>
        <button id="theme-btn" class="pill" type="button">Toggle theme</button>
      </div>
    </div>
  </header>
  <main>
    <div class="container">
      {body}
    </div>
  </main>
  <script src="/stock/assets/js/site.js"></script>
</body>
</html>
"""


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
            f"<div class='agent-card'><h3>{escape(key)}</h3><p>{escape(agent_outputs[key].summary)}</p></div>"
        )
    return "<div class='agent-grid'>" + "".join(cards) + "</div>"


def render_html(insight: DailyInsight, agent_outputs: dict[str, AgentOutput]) -> str:
    body = f"""
    <section class="hero">
      <div class="hero-card">
        <div class="report-pills">
          <span class="pill">{escape(insight.date)}</span>
          <span class="pill">{escape(insight.selected_asset.get("ticker", ""))}</span>
          <span class="pill">Confidence {escape(str(insight.confidence))}</span>
          <span class="pill">Risk {escape(str(insight.risk_level))}</span>
        </div>
        <h1 class="report-title-main">{escape(insight.title)}</h1>
        <p class="report-subtitle">{escape(insight.subtitle)}</p>
        {_list(insight.executive_summary)}
      </div>
    </section>

    <article class="report-shell">
      <section class="report-section">
        <h2>Decision Dashboard</h2>
        {_table(insight.dashboard, ["item", "conclusion", "reason"])}
      </section>

      <section class="report-section">
        <h2>Source Validation</h2>
        {_table(insight.source_table, ["source", "grade", "status", "reason", "url"])}
      </section>

      <section class="report-section">
        <h2>World Market and Scouting</h2>
        {_table(insight.macro_table, ["axis", "view", "impact"])}
        <h3>Primary Candidates</h3>
        {_table(insight.scouting_table, ["candidate", "ticker", "theme", "why_now", "status"])}
        <h3>Emerging and Less-Obvious Candidates</h3>
        {_table(insight.emerging_table, ["candidate", "stage", "quality_view", "value_view", "reason"])}
      </section>

      <section class="report-section">
        <h2>Price and Scenario</h2>
        {_table(insight.price_table, ["type", "price", "date", "vs_current", "comment"])}
        <h3>Range</h3>
        {_table(insight.range_table, ["period", "low", "high", "position", "comment"])}
        <h3>Scenario Targets</h3>
        {_table(insight.scenario_table, ["scenario", "target", "upside", "probability", "trigger"])}
      </section>

      <section class="report-section">
        <h2>Domain, Competition, and Risks</h2>
        {_table(insight.domain_table, ["item", "conclusion", "reason"])}
        <h3>Competition</h3>
        {_table(insight.competition_table, ["company", "strength", "weakness", "view"])}
        <h3>Fraud Guard</h3>
        {_table(insight.fraud_table, ["check", "status", "reason"])}
        <h3>Risk Map</h3>
        {_table(insight.risk_table, ["risk", "level", "reason", "response"])}
      </section>

      <section class="report-section">
        <h2>Debate and Verification</h2>
        {_table(insight.debate_table, ["point", "bull", "bear", "decision"])}
        <h3>Verification on Verification</h3>
        {_table(insight.verification_table, ["check", "status", "note"])}
        <h3>Final Review</h3>
        {_table(insight.final_review_table, ["check", "status", "note"])}
      </section>

      <section class="report-section">
        <h2>Probabilities and Future View</h2>
        {_table(insight.probability_table, ["outcome", "probability", "reason"])}
        <h3>Future View</h3>
        {_table(insight.future_view_table, ["horizon", "view", "reason"])}
      </section>

      <section class="report-section">
        <h2>Execution</h2>
        {_table(insight.buy_plan, ["step", "condition", "size", "reason"])}
        <h3>Sell Plan</h3>
        {_table(insight.sell_plan, ["step", "condition", "size", "reason"])}
        <h3>Final Action</h3>
        <p>{escape(insight.action)}</p>
        <h3>Catalysts</h3>
        {_list(insight.catalysts)}
        <h3>Watch Items</h3>
        {_list(insight.watch_items)}
      </section>

      <section class="report-section">
        <h2>Evidence and News</h2>
        {_table(insight.evidence_table, ["claim", "evidence"])}
        <h3>News Table</h3>
        {_table(insight.news_table, ["headline", "source", "quality", "impact", "judgment", "url"])}
        <h3>Rejected Alternatives</h3>
        {_list(insight.rejected_alternatives)}
      </section>

      <section class="report-section">
        <h2>Agent Trace</h2>
        {_agent_cards(agent_outputs)}
      </section>
    </article>
    """
    return _layout(insight.title, body)


def write_html_report(output_dir: str, insight: DailyInsight, content: str) -> str:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    target = path / f"{insight.date}_daily_master_report.html"
    target.write_text(content, encoding="utf-8")
    return str(target)


def write_site_assets(output_dir: str) -> None:
    css_path = Path(output_dir) / "assets" / "css"
    js_path = Path(output_dir) / "assets" / "js"
    css_path.mkdir(parents=True, exist_ok=True)
    js_path.mkdir(parents=True, exist_ok=True)
    (css_path / "style.css").write_text(SITE_CSS, encoding="utf-8")
    (js_path / "site.js").write_text(SITE_JS, encoding="utf-8")


def _report_cards(reports: list[dict[str, str]]) -> str:
    cards = []
    for report in sorted(reports, key=lambda item: item["label"], reverse=True):
        search_blob = " ".join(
            [
                report.get("label", ""),
                report.get("title", ""),
                report.get("ticker", ""),
                report.get("theme", ""),
                report.get("summary", ""),
            ]
        )
        cards.append(
            f"""
            <a class="report-card" data-report-card data-search="{escape(search_blob)}" href="{escape(report['link'])}">
              <div class="report-meta">
                <span>{escape(report.get("label", ""))}</span>
                <span>{escape(report.get("ticker", ""))}</span>
              </div>
              <div class="report-title">{escape(report.get("title", report.get("label", "")))}</div>
              <p class="report-desc">{escape(report.get("summary", ""))}</p>
            </a>
            """
        )
    return "".join(cards) if cards else "<p class='empty'>No reports yet.</p>"


def write_site_index(output_dir: str, reports: list[dict[str, str]]) -> str:
    cards_html = _report_cards(reports)
    reports_json = json.dumps(reports, ensure_ascii=False)

    body = f"""
    <section class="hero">
      <div class="hero-card">
        <h1 class="hero-title">Daily stock research archive</h1>
        <p class="hero-copy">Search first, then open cards. The home page is the archive: daily master reports, validated sources, risk views, and execution plans in one place.</p>
        <div class="hero-pills">
          <span class="pill">Blue theme</span>
          <span class="pill">Instant search</span>
          <span class="pill">Daily cards</span>
        </div>
      </div>
    </section>

    <section class="section-card">
      <h2 class="section-title">Report Cards</h2>
      <p class="muted">Press <code>/</code> to focus search. Results filter instantly on the page.</p>
      <div class="report-grid">
        {cards_html}
      </div>
    </section>

    <section class="section-card">
      <h2 class="section-title">Quick Links</h2>
      <div class="product-grid">
        <a href="/stock/reports/" class="product-card">
          <div class="product-title">Reports Archive</div>
          <p class="product-desc">Full list view for all generated daily reports</p>
        </a>
        <a href="https://github.com/agnusdei1207/stock/blob/main/STOCK.md" class="product-card">
          <div class="product-title">STOCK.md</div>
          <p class="product-desc">Methodology and report standard for the research engine</p>
        </a>
      </div>
    </section>

    <script id="report-data" type="application/json">{escape(reports_json)}</script>
    """
    target = Path(output_dir) / "index.html"
    target.write_text(_layout("stock daily reports", body), encoding="utf-8")
    return str(target)


def write_reports_index(output_dir: str, reports: list[dict[str, str]]) -> str:
    cards_html = _report_cards(reports)
    reports_json = json.dumps(reports, ensure_ascii=False)
    body = f"""
    <section class="hero">
      <div class="hero-card">
        <h1 class="hero-title">Reports archive</h1>
        <p class="hero-copy">Searchable card archive of daily stock master reports.</p>
      </div>
    </section>
    <section class="section-card">
      <h2 class="section-title">All Reports</h2>
      <div class="report-grid">{cards_html}</div>
    </section>
    <script id="report-data" type="application/json">{escape(reports_json)}</script>
    """
    target = Path(output_dir) / "reports" / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_layout("stock reports", body), encoding="utf-8")
    return str(target)


def publish_site_root(public_dir: str, repo_root: str) -> None:
    public_path = Path(public_dir)
    root_path = Path(repo_root)

    root_path.joinpath(".nojekyll").write_text("", encoding="utf-8")

    for relative in (
        "index.html",
        "assets/css/style.css",
        "assets/js/site.js",
        "reports/index.html",
    ):
        source = public_path / relative
        target = root_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    reports_public = public_path / "reports"
    reports_root = root_path / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    for html_file in reports_public.glob("*.html"):
        shutil.copy2(html_file, reports_root / html_file.name)
