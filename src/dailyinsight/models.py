from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DailyBrief:
    date: str
    world_market: dict[str, Any]
    headlines: list[dict[str, Any]]
    watchlist: list[str]
    notes: list[str]
    candidate_universe: list[dict[str, Any]]


@dataclass
class AgentOutput:
    agent: str
    summary: str
    bullets: list[str] = field(default_factory=list)
    scores: dict[str, int] = field(default_factory=dict)
    evidence: list[dict[str, str]] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class DailyInsight:
    date: str
    title: str
    subtitle: str
    executive_summary: list[str]
    action: str
    confidence: int
    risk_level: int
    dashboard: list[dict[str, str]]
    judgment_map: list[dict[str, str]]
    selected_asset: dict[str, str]
    source_table: list[dict[str, str]]
    macro_table: list[dict[str, str]]
    emerging_table: list[dict[str, str]]
    scouting_table: list[dict[str, str]]
    price_table: list[dict[str, str]]
    range_table: list[dict[str, str]]
    news_table: list[dict[str, str]]
    domain_table: list[dict[str, str]]
    competition_table: list[dict[str, str]]
    fraud_table: list[dict[str, str]]
    risk_table: list[dict[str, str]]
    debate_table: list[dict[str, str]]
    verification_table: list[dict[str, str]]
    final_review_table: list[dict[str, str]]
    probability_table: list[dict[str, str]]
    future_view_table: list[dict[str, str]]
    scenario_table: list[dict[str, str]]
    buy_plan: list[dict[str, str]]
    sell_plan: list[dict[str, str]]
    catalysts: list[str]
    watch_items: list[str]
    evidence_table: list[dict[str, str]]
    rejected_alternatives: list[str]
