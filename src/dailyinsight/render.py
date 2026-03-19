from __future__ import annotations

import re
from pathlib import Path

from .models import AgentOutput, DailyInsight


def _bar(score: int, width: int = 10) -> str:
    filled = max(0, min(width, round(score / 100 * width)))
    return "█" * filled + "░" * (width - filled)


def _parse_money(value: str) -> float:
    cleaned = re.sub(r"[^0-9.]", "", value or "")
    return float(cleaned) if cleaned else 0.0


def _render_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return lines


def _price_position_chart(insight: DailyInsight) -> list[str]:
    if not insight.price_table:
        return []
    current = next((row for row in insight.price_table if row.get("type") == "Current"), {})
    ath = next((row for row in insight.price_table if row.get("type") == "ATH"), {})
    low_52 = next((row for row in insight.price_table if row.get("type") == "52W Low"), {})
    high_52 = next((row for row in insight.price_table if row.get("type") == "52W High"), {})

    current_value = _parse_money(current.get("price", "0"))
    low_value = _parse_money(low_52.get("price", "0"))
    high_value = _parse_money(high_52.get("price", "0"))
    ath_value = _parse_money(ath.get("price", "0"))

    pos = 0
    if high_value > low_value:
        pos = round(((current_value - low_value) / (high_value - low_value)) * 20)
        pos = max(0, min(20, pos))

    line = ["-"] * 21
    line[pos] = "*"
    return [
        "```text",
        "[Price Position Map]",
        "",
        "52W Low              Current                 52W High                ATH",
        "|" + "".join(line) + "|",
        f"{low_value:>6.2f}              {current_value:>6.2f}                  {high_value:>6.2f}                {ath_value:>6.2f}",
        "```",
    ]


def _range_chart(insight: DailyInsight) -> list[str]:
    lines = ["```text", "[Range Compression / Expansion]", ""]
    for row in insight.range_table:
        label = row.get("period", "")
        pos = row.get("position", "")
        if "high" in pos:
            bar = "|--------------*----|"
        elif "mid" in pos:
            bar = "|--------*---------|"
        else:
            bar = "|---*--------------|"
        lines.append(f"{label:<4} {bar}")
    lines.append("```")
    return lines


def _source_chart(insight: DailyInsight) -> list[str]:
    grade_map = {"S": 10, "A": 9, "B": 6, "C": 3, "D": 1}
    lines = ["```text", "[Source Quality Score]", ""]
    for row in insight.source_table:
        score = grade_map.get(row.get("grade", "C"), 3) * 10
        lines.append(f"{row.get('source', ''):<16} {_bar(score)} {row.get('grade', '')}")
    lines.append("```")
    return lines


def _probability_chart(insight: DailyInsight) -> list[str]:
    lines = ["```text", "[Probability Board]", ""]
    for row in insight.probability_table:
        prob_raw = row.get("probability", "0").replace("%", "")
        score = int(prob_raw) if prob_raw.isdigit() else 0
        lines.append(f"{row.get('outcome', '')[:26]:<26} {_bar(score)} {row.get('probability', '')}")
    lines.append("```")
    return lines


def _scenario_chart(insight: DailyInsight) -> list[str]:
    lines = ["```text", "[Scenario Targets]", ""]
    for row in insight.scenario_table:
        upside = row.get("upside", "0").replace("%", "").replace("+", "")
        score = 0
        try:
            score = min(100, max(0, int(float(upside) * 2)))
        except ValueError:
            score = 0
        lines.append(f"{row.get('scenario', ''):<5} {_bar(score)} {row.get('target', '')} ({row.get('upside', '')})")
    lines.append("```")
    return lines


def _action_tree() -> list[str]:
    return [
        "```text",
        "[Execution Tree]",
        "",
        "Current idea",
        "  |",
        "  +-- Source quality weak? ---- yes --> reject / re-check",
        "  |",
        "  +-- Thesis intact? --------- no ---> remove from active list",
        "  |",
        "  +-- Pullback into plan? ---- yes --> staged buy",
        "  |",
        "  +-- Catalysts confirmed? --- yes --> add / hold",
        "  |",
        "  +-- Base/Bull target hit? -- yes --> trim / de-risk",
        "```",
    ]


def render_markdown(insight: DailyInsight, agent_outputs: dict[str, AgentOutput]) -> str:
    lines: list[str] = []
    lines.append(f"# {insight.date} Daily Master Report")
    lines.append("")
    lines.append(f"## {insight.title}")
    lines.append("")
    lines.append(insight.subtitle)
    lines.append("")

    lines.append("## Core Insight")
    lines.append("")
    for item in insight.executive_summary:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Decision Dashboard")
    lines.append("")
    lines.extend(_render_table(insight.dashboard, ["item", "conclusion", "reason"]))
    lines.append("")
    lines.extend(
        [
            "```text",
            "[Daily Signal Board]",
            "",
            f"Confidence  {_bar(insight.confidence)} {insight.confidence}",
            f"Risk        {_bar(insight.risk_level)} {insight.risk_level}",
            "```",
        ]
    )
    lines.append("")

    lines.append("## Judgment Map")
    lines.append("")
    lines.extend(_render_table(insight.judgment_map, ["judgment", "conclusion", "data", "source"]))
    lines.append("")

    lines.append("## Selected Asset")
    lines.append("")
    lines.extend(_render_table([insight.selected_asset], ["name", "ticker", "market", "theme", "current_price"]))
    lines.append("")

    lines.append("## Source Validation")
    lines.append("")
    lines.extend(_render_table(insight.source_table, ["source", "grade", "status", "reason", "url"]))
    lines.append("")
    lines.extend(_source_chart(insight))
    lines.append("")

    lines.append("## World Market and Regime")
    lines.append("")
    lines.extend(_render_table(insight.macro_table, ["axis", "view", "impact"]))
    lines.append("")

    lines.append("## Global Scouting")
    lines.append("")
    lines.extend(_render_table(insight.scouting_table, ["candidate", "ticker", "theme", "why_now", "status"]))
    lines.append("")

    lines.append("## Emerging and Less-Obvious Candidates")
    lines.append("")
    lines.extend(_render_table(insight.emerging_table, ["candidate", "stage", "quality_view", "value_view", "reason"]))
    lines.append("")

    lines.append("## Price Dashboard")
    lines.append("")
    lines.extend(_render_table(insight.price_table, ["type", "price", "date", "vs_current", "comment"]))
    lines.append("")
    lines.extend(_price_position_chart(insight))
    lines.append("")

    lines.append("## Range Analysis")
    lines.append("")
    lines.extend(_render_table(insight.range_table, ["period", "low", "high", "position", "comment"]))
    lines.append("")
    lines.extend(_range_chart(insight))
    lines.append("")

    lines.append("## News and Source-Linked Catalysts")
    lines.append("")
    lines.extend(_render_table(insight.news_table, ["headline", "source", "quality", "impact", "judgment", "url"]))
    lines.append("")

    lines.append("## Domain Insight")
    lines.append("")
    lines.extend(_render_table(insight.domain_table, ["item", "conclusion", "reason"]))
    lines.append("")

    lines.append("## Competition and Positioning")
    lines.append("")
    lines.extend(_render_table(insight.competition_table, ["company", "strength", "weakness", "view"]))
    lines.append("")

    lines.append("## Quality and Fraud Guard")
    lines.append("")
    lines.extend(_render_table(insight.fraud_table, ["check", "status", "reason"]))
    lines.append("")

    lines.append("## Bull vs Bear Debate")
    lines.append("")
    lines.extend(_render_table(insight.debate_table, ["point", "bull", "bear", "decision"]))
    lines.append("")

    lines.append("## Verification on Verification")
    lines.append("")
    lines.extend(_render_table(insight.verification_table, ["check", "status", "note"]))
    lines.append("")

    lines.append("## Final Report Review")
    lines.append("")
    lines.extend(_render_table(insight.final_review_table, ["check", "status", "note"]))
    lines.append("")

    lines.append("## Probability and Future View")
    lines.append("")
    lines.extend(_render_table(insight.probability_table, ["outcome", "probability", "reason"]))
    lines.append("")
    lines.extend(_probability_chart(insight))
    lines.append("")
    lines.extend(_render_table(insight.future_view_table, ["horizon", "view", "reason"]))
    lines.append("")

    lines.append("## Evidence Chain")
    lines.append("")
    lines.extend(_render_table(insight.evidence_table, ["claim", "evidence"]))
    lines.append("")

    lines.append("## Risk Map")
    lines.append("")
    lines.extend(_render_table(insight.risk_table, ["risk", "level", "reason", "response"]))
    lines.append("")

    lines.append("## Scenario Targets")
    lines.append("")
    lines.extend(_render_table(insight.scenario_table, ["scenario", "target", "upside", "probability", "trigger"]))
    lines.append("")
    lines.extend(_scenario_chart(insight))
    lines.append("")

    lines.append("## Buy Plan")
    lines.append("")
    lines.extend(_render_table(insight.buy_plan, ["step", "condition", "size", "reason"]))
    lines.append("")

    lines.append("## Sell Plan")
    lines.append("")
    lines.extend(_render_table(insight.sell_plan, ["step", "condition", "size", "reason"]))
    lines.append("")
    lines.extend(_action_tree())
    lines.append("")

    lines.append("## Catalysts")
    lines.append("")
    for idx, catalyst in enumerate(insight.catalysts, start=1):
        lines.append(f"- T+{idx}: {catalyst}")
    lines.append("")

    lines.append("## Watch Items")
    lines.append("")
    for item in insight.watch_items:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Rejected Alternatives")
    lines.append("")
    for item in insight.rejected_alternatives:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Agent Trace")
    lines.append("")
    lines.extend(_render_table(
        [
            {"agent": "source_gate", "summary": agent_outputs["source_gate"].summary},
            {"agent": "emerging_scout", "summary": agent_outputs["emerging_scout"].summary},
            {"agent": "scout", "summary": agent_outputs["scout"].summary},
            {"agent": "macro", "summary": agent_outputs["macro"].summary},
            {"agent": "domain", "summary": agent_outputs["domain"].summary},
            {"agent": "fraud_guard", "summary": agent_outputs["fraud_guard"].summary},
            {"agent": "bull", "summary": agent_outputs["bull"].summary},
            {"agent": "bear", "summary": agent_outputs["bear"].summary},
            {"agent": "reflection", "summary": agent_outputs["reflection"].summary},
            {"agent": "strategy", "summary": agent_outputs["strategy"].summary},
            {"agent": "report_verifier", "summary": agent_outputs["report_verifier"].summary},
        ],
        ["agent", "summary"],
    ))
    lines.append("")

    lines.append("## Final Action")
    lines.append("")
    lines.append(insight.action)
    lines.append("")
    return "\n".join(lines)


def write_report(output_dir: str, insight: DailyInsight, content: str) -> str:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    target = path / f"{insight.date}_daily_master_report.md"
    target.write_text(content, encoding="utf-8")
    return str(target)
