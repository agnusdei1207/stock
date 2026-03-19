from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass

from .config import AppConfig


class LLMError(RuntimeError):
    pass


@dataclass
class LLMClient:
    config: AppConfig

    def complete_json(self, prompt: str) -> dict:
        if not self.config.api_key:
            raise LLMError("ANTHROPIC_API_KEY is required for live mode")

        url = self.config.base_url.rstrip("/") + "/v1/messages"
        body = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": 0.2,
            "system": "You are a concise financial research orchestrator. Output valid JSON only.",
            "messages": [{"role": "user", "content": prompt}],
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        try:
            blocks = payload["content"]
            text_blocks = [block["text"] for block in blocks if block.get("type") == "text"]
            content = "\n".join(text_blocks)
            return json.loads(content)
        except Exception as exc:
            raise LLMError(f"Invalid LLM response: {payload}") from exc


class MockLLMClient:
    def complete_json(self, prompt: str) -> dict:
        if "SourceGateAgent" in prompt:
            return {
                "summary": "High-confidence inputs survive only if they are attributable, technical, and cross-checkable. Reuters/FT/Hacker News/Techmeme-style inputs remain; rumor sludge is rejected.",
                "accepted_sources": ["Reuters", "FT", "Techmeme", "Hacker News", "company IR"],
                "rejected_sources": ["unattributed clickbait", "rumor aggregators", "bait headlines without numbers"],
                "source_table": [
                    {"source": "Reuters", "grade": "A", "status": "accepted", "reason": "attributable reporting", "url": "https://www.reuters.com/"},
                    {"source": "FT", "grade": "A", "status": "accepted", "reason": "industry context and sourcing", "url": "https://www.ft.com/"},
                    {"source": "Techmeme", "grade": "B", "status": "accepted-with-check", "reason": "good routing layer but not primary evidence", "url": "https://www.techmeme.com/"},
                    {"source": "Hacker News", "grade": "B", "status": "accepted-with-check", "reason": "useful technical signal, not proof", "url": "https://news.ycombinator.com/"},
                    {"source": "bait aggregator", "grade": "D", "status": "rejected", "reason": "low attribution and hallucination risk", "url": "n/a"},
                ],
                "verification_rules": [
                    "No single headline is enough",
                    "Need attributable source plus domain logic",
                    "Need data linkage before action",
                ],
            }
        if "EmergingScoutAgent" in prompt:
            return {
                "summary": "Early-stage or less-followed names are worth watching only when they survive fraud and quality filters. The interesting ones are infrastructure-adjacent enablers, not promotional dream sellers.",
                "emerging_table": [
                    {"candidate": "Emerging CoolingCo", "stage": "early public", "quality_view": "watch", "value_view": "possible", "reason": "real bottleneck exposure but limited proof yet"},
                    {"candidate": "GridEdge Systems", "stage": "small cap", "quality_view": "watch", "value_view": "possible", "reason": "infrastructure relevance with still-thin coverage"},
                    {"candidate": "AI Vapor Story", "stage": "story stock", "quality_view": "avoid", "value_view": "weak", "reason": "promotional language exceeds monetization evidence"},
                ],
                "evidence": [
                    {"claim": "newer ideas need stricter filters", "detail": "small or new does not mean valuable"},
                    {"claim": "best early ideas are still bottleneck-linked", "detail": "real demand path matters more than hype"},
                ],
            }
        if "ScoutAgent" in prompt:
            return {
                "summary": "The most promising area remains AI physical bottlenecks, especially power and cooling suppliers that monetize capex before many obvious software narratives do.",
                "themes": [
                    "AI power and cooling bottlenecks",
                    "Semicap second-order suppliers",
                    "Industrial automation tied to productivity capex",
                ],
                "scouting_table": [
                    {"candidate": "Vertiv", "ticker": "VRT", "theme": "AI power/cooling", "why_now": "backlog plus bottleneck exposure", "status": "selected"},
                    {"candidate": "Eaton", "ticker": "ETN", "theme": "electrical infrastructure", "why_now": "grid and power equipment leverage", "status": "watch"},
                    {"candidate": "Camtek", "ticker": "CAMT", "theme": "semicap inspection", "why_now": "second-order semicap leverage", "status": "watch"},
                ],
                "selected_asset": {
                    "name": "Vertiv",
                    "ticker": "VRT",
                    "market": "USA",
                    "theme": "AI power and cooling bottleneck",
                    "current_price": "$96.40",
                },
                "evidence": [
                    {"claim": "Theme still matters", "detail": "AI buildout hits physical constraints"},
                    {"claim": "Better discovery value", "detail": "less crowded than headline mega-cap AI"},
                ],
            }
        if "MacroAgent" in prompt:
            return {
                "summary": "The current regime favors earnings-visible infrastructure rather than long-duration concept stocks, so a bottleneck supplier fits better than a pure narrative name.",
                "bullets": [
                    "Higher-for-longer rates punish distant cash flows",
                    "Capex-linked infrastructure remains favored if backlog and margins hold",
                    "Selective risk-on means not every AI label works equally well",
                ],
                "macro_table": [
                    {"axis": "Rates", "view": "restrictive but stable", "impact": "supports revenue-visible infrastructure"},
                    {"axis": "Dollar", "view": "firm", "impact": "mixed, but quality still wins"},
                    {"axis": "Sector rotation", "view": "selective AI infra", "impact": "second-order winners still viable"},
                ],
                "evidence": [{"signal": "regime", "detail": "market prefers clearer monetization"}],
            }
        if "DomainAgent" in prompt:
            return {
                "summary": "The durable edge is not just compute demand but who clears the deployment bottleneck first. Power density, thermal management, and electrical buildout sit close to hard deployment constraints.",
                "bullets": [
                    "Power and thermal limits slow deployment regardless of chip appetite",
                    "Bottleneck vendors can gain pricing power before downstream beneficiaries",
                    "The market still underweights physical constraints versus abstract AI demand",
                ],
                "domain_table": [
                    {"item": "Bottleneck", "conclusion": "high importance", "reason": "power density and cooling cap deployment"},
                    {"item": "Pricing power", "conclusion": "improving", "reason": "scarcity plus urgency"},
                    {"item": "Customer need", "conclusion": "structural", "reason": "AI campuses require physical buildout"},
                ],
                "competition_table": [
                    {"company": "Vertiv", "strength": "cooling and power integration", "weakness": "valuation already richer", "view": "leader"},
                    {"company": "Eaton", "strength": "electrical breadth", "weakness": "broader industrial mix", "view": "quality peer"},
                    {"company": "Schneider", "strength": "global infrastructure reach", "weakness": "less pure-play", "view": "large diversified peer"},
                ],
                "evidence": [
                    {"signal": "deployment", "detail": "AI demand converts only when sites can actually run"},
                    {"signal": "scarcity", "detail": "lead times matter in constrained infrastructure"},
                ],
                "scores": {"structural": 86, "timing": 77, "crowding": 61},
            }
        if "FraudGuardAgent" in prompt:
            return {
                "summary": "The selected idea does not look like a classic fraud setup, but it still has quality risks that must be monitored. The main danger is overpromotion of a real theme rather than outright fake economics.",
                "fraud_table": [
                    {"check": "promotional tone", "status": "medium watch", "reason": "hot theme can attract exaggerated narratives"},
                    {"check": "monetization clarity", "status": "pass", "reason": "real infrastructure spend ties to revenue"},
                    {"check": "customer dependence", "status": "watch", "reason": "few buyers can distort perception"},
                    {"check": "financial reality", "status": "pass", "reason": "theme maps to real capex rather than vague TAM talk"},
                ],
                "evidence": [
                    {"claim": "not pure story equity", "detail": "revenue path is more tangible than many AI narrative names"},
                    {"claim": "still needs discipline", "detail": "hot thematic exposure can invite lazy overstatement"},
                ],
                "scores": {"fraud_risk": 31, "quality_risk": 48},
            }
        if "BullAgent" in prompt:
            return {
                "summary": "Bull case: this is the cleaner way to monetize AI buildout because it sits at a real physical choke point and converts capex into nearer-term revenue.",
                "bullets": [
                    "backlog visibility is better than story-stock revenue hope",
                    "physical bottlenecks usually reprice late but hard",
                    "customers cannot skip power and cooling to deploy AI capacity",
                ],
                "evidence": [
                    {"claim": "Revenue visibility", "detail": "bottleneck infrastructure is closer to actual capex spend"},
                    {"claim": "Strategic importance", "detail": "deployment fails if power/cooling fails"},
                ],
                "scores": {"upside": 79, "clarity": 82},
            }
        if "BearAgent" in prompt:
            return {
                "summary": "Bear case: the theme is right but the timing may be messy. Some names have already re-rated, backlog optimism can be in price, and AI capex digestion would hit second-order beneficiaries hard.",
                "bullets": [
                    "valuation can outrun fundamentals",
                    "customer concentration can distort quarter-to-quarter reads",
                    "capex pauses or delays hurt harder than the narrative suggests",
                ],
                "risk_table": [
                    {"risk": "valuation", "level": "high", "reason": "quality premium already expanded", "response": "do not chase vertical moves"},
                    {"risk": "customer concentration", "level": "high", "reason": "few buyers dominate orders", "response": "watch backlog and large-order commentary"},
                    {"risk": "AI capex digestion", "level": "medium", "reason": "deployment can pause after bursts", "response": "prefer staged entries"},
                ],
                "evidence": [
                    {"claim": "Already known theme", "detail": "some infrastructure names are no longer obscure"},
                    {"claim": "fragile timing", "detail": "order timing matters when valuation is elevated"},
                ],
                "scores": {"downside": 67, "fragility": 64},
            }
        if "ReflectionAgent" in prompt:
            return {
                "summary": "After debate, the theme still stands, but conviction should be reduced slightly because the thesis is stronger than the exact entry timing. Source quality is good enough, but price discipline is mandatory.",
                "debate_table": [
                    {"point": "AI bottleneck is real", "bull": "structural constraint", "bear": "may already be known", "decision": "keep thesis, reduce enthusiasm"},
                    {"point": "better than mega-cap AI", "bull": "less crowded", "bear": "some leaders already re-rated", "decision": "prefer ranked basket, not blind single-name chase"},
                    {"point": "news quality", "bull": "sources attributable", "bear": "HN/Techmeme are routing layers", "decision": "require primary-source follow-through"},
                ],
                "verification_table": [
                    {"check": "source quality", "status": "pass", "note": "A/B sources only"},
                    {"check": "hallucination risk", "status": "watch", "note": "technical commentary needs primary confirmation"},
                    {"check": "thesis-data link", "status": "pass", "note": "bottleneck logic matches monetization path"},
                    {"check": "entry timing confidence", "status": "caution", "note": "valuation may be ahead of perfect entry"},
                ],
                "confidence_adjustment": -4,
                "risk_adjustment": 6,
                "bullets": [
                    "keep thesis",
                    "tighten entry discipline",
                    "require primary-source confirmation behind routing/news aggregation",
                ],
            }
        if "StrategyAgent" in prompt:
            return {
                "summary": "The right move is not all-in buying but disciplined ranking and staged entry into infrastructure bottleneck names, starting with the cleanest backlog and pricing-power profile.",
                "price_table": [
                    {"type": "Current", "price": "$96.40", "date": "2026-03-19", "vs_current": "0.0%", "comment": "decision anchor"},
                    {"type": "ATH", "price": "$110.00", "date": "2026-02-11", "vs_current": "-12.4%", "comment": "shows prior peak"},
                    {"type": "ATL", "price": "$8.00", "date": "2020-03-18", "vs_current": "+1105.0%", "comment": "long-cycle context"},
                    {"type": "52W High", "price": "$110.00", "date": "2026-02-11", "vs_current": "-12.4%", "comment": "recent ceiling"},
                    {"type": "52W Low", "price": "$58.20", "date": "2025-04-08", "vs_current": "+65.6%", "comment": "recent floor"},
                ],
                "range_table": [
                    {"period": "1M", "low": "$88.00", "high": "$104.00", "position": "mid-high", "comment": "near-term momentum intact"},
                    {"period": "3M", "low": "$79.00", "high": "$110.00", "position": "upper-mid", "comment": "not cheap, not euphoric peak"},
                    {"period": "6M", "low": "$72.00", "high": "$110.00", "position": "upper", "comment": "trend still constructive"},
                    {"period": "1Y", "low": "$58.20", "high": "$110.00", "position": "upper", "comment": "valuation discipline required"},
                    {"period": "ALL", "low": "$8.00", "high": "$110.00", "position": "high", "comment": "long upcycle winner"},
                ],
                "scenario_table": [
                    {"scenario": "Bull", "target": "$122", "upside": "+27%", "probability": "25%", "trigger": "backlog and margins hold"},
                    {"scenario": "Base", "target": "$108", "upside": "+12%", "probability": "50%", "trigger": "steady execution"},
                    {"scenario": "Bear", "target": "$82", "upside": "-15%", "probability": "25%", "trigger": "capex digestion or rerating"},
                ],
                "buy_plan": [
                    {"step": "1st buy", "condition": "$90-$93 or quality pullback", "size": "30%", "reason": "starter position only"},
                    {"step": "2nd buy", "condition": "post-earnings confirmation", "size": "30%", "reason": "execution validated"},
                    {"step": "3rd buy", "condition": "support holds after volatility", "size": "40%", "reason": "higher confidence add"},
                ],
                "sell_plan": [
                    {"step": "1st trim", "condition": "near base target / stretched momentum", "size": "25%", "reason": "de-risk"},
                    {"step": "2nd trim", "condition": "near bull target", "size": "25%", "reason": "lock gains"},
                    {"step": "thesis break", "condition": "backlog weakens or AI capex stalls", "size": "remaining", "reason": "exit thesis failure"},
                ],
                "catalysts": [
                    "hyperscaler capex commentary",
                    "company backlog and margin update",
                    "data-center permitting and power-delivery developments",
                ],
                "watch_items": [
                    "book-to-bill",
                    "gross margin progression",
                    "customer concentration",
                    "order timing versus valuation",
                ],
            }
        if "ReportVerifierAgent" in prompt:
            return {
                "summary": "The report is directionally strong and insight-dense, but the right final posture is still disciplined rather than evangelical. Confidence should come down a touch and risk up slightly to reflect entry uncertainty and verification conservatism.",
                "final_review_table": [
                    {"check": "signal density", "status": "pass", "note": "few fluff sections"},
                    {"check": "source grounding", "status": "pass", "note": "URLs and source grades retained"},
                    {"check": "future-view realism", "status": "pass", "note": "future edge tied to structural bottlenecks"},
                    {"check": "overclaim risk", "status": "watch", "note": "do not turn good theme into certainty"},
                ],
                "confidence_adjustment": -2,
                "risk_adjustment": 2,
                "bullets": [
                    "keep high signal",
                    "avoid certainty theater",
                    "preserve verification-first posture",
                ],
            }
        return {
            "title": "Daily Master Report: AI deployment bottlenecks still offer a better edge than the loudest AI narrative",
            "subtitle": "Focus on power and cooling infrastructure where AI demand turns into real revenue earlier and more visibly.",
            "executive_summary": [
                "The best daily idea is still AI physical infrastructure, not generic AI excitement.",
                "Power and cooling are real deployment chokepoints, which makes monetization clearer.",
                "The thesis is good, but entry timing matters because valuation is no longer cheap.",
            ],
            "action": "Rank and monitor AI power/cooling leaders first, then build exposure through staged entries rather than momentum chasing.",
            "confidence": 72,
            "risk_level": 69,
            "dashboard": [
                {"item": "Final action", "conclusion": "staged buy / ranked watch", "reason": "good thesis, imperfect entry"},
                {"item": "Attractiveness", "conclusion": "A-", "reason": "strong structural logic"},
                {"item": "Risk", "conclusion": "high", "reason": "valuation and timing sensitivity"},
                {"item": "Time horizon", "conclusion": "medium-term", "reason": "6-12 month execution window"},
                {"item": "Catalyst strength", "conclusion": "high", "reason": "earnings and backlog visibility"},
                {"item": "Source quality", "conclusion": "good with checks", "reason": "A/B sources retained"},
            ],
            "judgment_map": [
                {"judgment": "theme quality", "conclusion": "strong", "data": "hard bottleneck + capex visibility", "source": "Reuters/FT/technical routing"},
                {"judgment": "timing", "conclusion": "mixed", "data": "52W upper-band position", "source": "price snapshot"},
                {"judgment": "risk", "conclusion": "elevated", "data": "rerated multiples + concentration", "source": "peer and thesis review"},
            ],
            "news_table": [
                {"headline": "Hyperscaler capex still favors infrastructure", "source": "Reuters", "quality": "A", "impact": "high", "judgment": "supports thesis", "url": "https://www.reuters.com/"},
                {"headline": "Cooling and utility vendors see AI demand", "source": "FT", "quality": "A", "impact": "high", "judgment": "supports bottleneck logic", "url": "https://www.ft.com/"},
                {"headline": "Techmeme / HN technical discussion", "source": "Techmeme/HN", "quality": "B", "impact": "medium", "judgment": "useful signal, not final proof", "url": "https://www.techmeme.com/"},
            ],
            "evidence_table": [
                {"claim": "Theme fits regime", "evidence": "market rewards revenue-visible infra over distant narratives"},
                {"claim": "Bottleneck is structural", "evidence": "AI deployment is constrained by power and cooling, not just chip supply"},
                {"claim": "Still actionable", "evidence": "second-order infrastructure remains less crowded than headline mega-cap AI"},
            ],
            "probability_table": [
                {"outcome": "Structural thesis remains valid", "probability": "78%", "reason": "physical bottleneck logic is durable and not dependent on a single headline"},
                {"outcome": "Near-term entry timing is favorable", "probability": "54%", "reason": "good theme but valuation and positioning reduce precision"},
                {"outcome": "Market is still underpricing second-order winners", "probability": "61%", "reason": "discovery edge remains outside the loudest mega-cap AI names"},
            ],
            "future_view_table": [
                {"horizon": "3 months", "view": "execution beats narrative", "reason": "market demands backlog and margin proof"},
                {"horizon": "6-12 months", "view": "power-density winners keep monetizing", "reason": "AI deployment remains infrastructure constrained"},
                {"horizon": "1-3 years", "view": "the winners will be who turn scarce deployment inputs into recurring pricing power", "reason": "future value moves toward bottleneck owners, not just compute brands"},
            ],
            "rejected_alternatives": [
                "story stocks with weak near-term monetization",
                "headline AI names with lower discovery edge",
                "low-quality rumor-driven names without attributable sourcing",
            ],
        }
