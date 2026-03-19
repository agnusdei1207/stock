from __future__ import annotations

from .input_loader import load_brief
from .models import AgentOutput, DailyInsight
from .prompts import (
    bear_prompt,
    bull_prompt,
    domain_prompt,
    emerging_scout_prompt,
    fraud_guard_prompt,
    macro_prompt,
    reflection_prompt,
    report_verifier_prompt,
    scout_prompt,
    source_gate_prompt,
    strategy_prompt,
    synthesizer_prompt,
)


class DailyInsightOrchestrator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def _agent_output(self, name: str, payload: dict) -> AgentOutput:
        return AgentOutput(
            agent=name,
            summary=payload.get("summary", ""),
            bullets=payload.get("bullets", []),
            scores=payload.get("scores", {}),
            evidence=payload.get("evidence", []),
            payload=payload,
        )

    def run(self, input_path: str) -> tuple[DailyInsight, dict[str, AgentOutput]]:
        brief = load_brief(input_path)

        source_raw = self.llm.complete_json(source_gate_prompt(brief))
        source_gate = self._agent_output("source_gate", source_raw)

        emerging_raw = self.llm.complete_json(emerging_scout_prompt(brief, source_gate.summary))
        emerging = self._agent_output("emerging_scout", emerging_raw)

        scout_raw = self.llm.complete_json(scout_prompt(brief, source_gate.summary, emerging.summary))
        scout = self._agent_output("scout", scout_raw)
        selected_asset = scout_raw.get("selected_asset", {})

        macro_raw = self.llm.complete_json(macro_prompt(brief, scout.summary))
        macro = self._agent_output("macro", macro_raw)

        domain_raw = self.llm.complete_json(domain_prompt(brief, selected_asset))
        domain = self._agent_output("domain", domain_raw)

        fraud_raw = self.llm.complete_json(fraud_guard_prompt(brief, selected_asset))
        fraud = self._agent_output("fraud_guard", fraud_raw)

        bull_raw = self.llm.complete_json(bull_prompt(brief, selected_asset, domain.summary))
        bull = self._agent_output("bull", bull_raw)

        bear_raw = self.llm.complete_json(bear_prompt(brief, selected_asset, domain.summary))
        bear = self._agent_output("bear", bear_raw)

        reflection_raw = self.llm.complete_json(
            reflection_prompt(brief, bull.summary, bear.summary, source_gate.summary, fraud.summary)
        )
        reflection = self._agent_output("reflection", reflection_raw)

        strategy_raw = self.llm.complete_json(
            strategy_prompt(brief, selected_asset, bear.summary, reflection.summary)
        )
        strategy = self._agent_output("strategy", strategy_raw)

        synth_raw = self.llm.complete_json(
            synthesizer_prompt(
                brief,
                source_gate.summary,
                emerging.summary,
                scout.summary,
                macro.summary,
                domain.summary,
                fraud.summary,
                bull.summary,
                bear.summary,
                reflection.summary,
                strategy.summary,
            )
        )
        synth = self._agent_output("synthesizer", synth_raw)
        draft_summary = " | ".join(
            [synth_raw.get("title", ""), synth_raw.get("subtitle", "")]
            + synth_raw.get("executive_summary", [])
        )

        base_confidence = int(synth_raw.get("confidence", 50))
        base_risk = int(synth_raw.get("risk_level", 50))
        confidence = max(0, min(100, base_confidence + int(reflection_raw.get("confidence_adjustment", 0))))
        risk_level = max(0, min(100, base_risk + int(reflection_raw.get("risk_adjustment", 0))))

        final_verify_raw = self.llm.complete_json(
            report_verifier_prompt(brief, draft_summary, synth_raw["action"], confidence, risk_level)
        )
        final_verify = self._agent_output("report_verifier", final_verify_raw)
        confidence = max(0, min(100, confidence + int(final_verify_raw.get("confidence_adjustment", 0))))
        risk_level = max(0, min(100, risk_level + int(final_verify_raw.get("risk_adjustment", 0))))

        insight = DailyInsight(
            date=brief.date,
            title=synth_raw["title"],
            subtitle=synth_raw["subtitle"],
            executive_summary=synth_raw.get("executive_summary", []),
            action=synth_raw["action"],
            confidence=confidence,
            risk_level=risk_level,
            dashboard=synth_raw.get("dashboard", []),
            judgment_map=synth_raw.get("judgment_map", []),
            selected_asset={k: str(v) for k, v in selected_asset.items()},
            source_table=source_raw.get("source_table", []),
            macro_table=macro_raw.get("macro_table", []),
            emerging_table=emerging_raw.get("emerging_table", []),
            scouting_table=scout_raw.get("scouting_table", []),
            price_table=strategy_raw.get("price_table", []),
            range_table=strategy_raw.get("range_table", []),
            news_table=synth_raw.get("news_table", []),
            domain_table=domain_raw.get("domain_table", []),
            competition_table=domain_raw.get("competition_table", []),
            fraud_table=fraud_raw.get("fraud_table", []),
            risk_table=bear_raw.get("risk_table", []),
            debate_table=reflection_raw.get("debate_table", []),
            verification_table=reflection_raw.get("verification_table", []),
            final_review_table=final_verify_raw.get("final_review_table", []),
            probability_table=synth_raw.get("probability_table", []),
            future_view_table=synth_raw.get("future_view_table", []),
            scenario_table=strategy_raw.get("scenario_table", []),
            buy_plan=strategy_raw.get("buy_plan", []),
            sell_plan=strategy_raw.get("sell_plan", []),
            catalysts=strategy_raw.get("catalysts", []),
            watch_items=strategy_raw.get("watch_items", []),
            evidence_table=synth_raw.get("evidence_table", []),
            rejected_alternatives=synth_raw.get("rejected_alternatives", []),
        )

        return insight, {
            "source_gate": source_gate,
            "emerging_scout": emerging,
            "scout": scout,
            "macro": macro,
            "domain": domain,
            "fraud_guard": fraud,
            "bull": bull,
            "bear": bear,
            "reflection": reflection,
            "strategy": strategy,
            "synthesizer": synth,
            "report_verifier": final_verify,
        }
