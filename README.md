# stock

Daily investing master-report agent orchestration.

This project is not an auto-trading bot. It is a research pipeline that turns a daily market brief into one detailed daily master report with explicit evidence, source validation, debate, reflection, risk, probabilities, and action framing.

## Design

Inspired by:

- `TradingAgents-CN`: role-based market analysis
- `../Pentesting`: lightweight orchestration, explicit stages, report-first output

Pipeline:

1. `SourceGateAgent`
   Filters weak or hallucination-prone news and keeps only attributable sources.
2. `ScoutAgent`
   Finds candidate themes, second-order beneficiaries, and a primary asset.
3. `MacroAgent`
   Adds world-market context, regime, and cross-asset framing.
4. `DomainAgent`
   Explains why the theme matters structurally, not just because it is in the news.
5. `BullAgent`
   Builds the strongest positive thesis.
6. `BearAgent`
   Attacks the thesis and forces downside conditions.
7. `ReflectionAgent`
   Re-checks source quality, logic quality, and overconfidence.
8. `StrategyAgent`
   Builds price, scenario, buy, and sell plans.
9. `SynthesizerAgent`
   Writes the final STOCK.md-style daily master report.

## Quick Start

Create a virtualenv if you want isolation, then run:

```bash
python3 -m dailyinsight.cli run \
  --input examples/sample_brief.json \
  --output reports \
  --mode mock
```

This generates a markdown report under `reports/`.

## Live LLM Mode

The live mode reads the existing Anthropic-compatible GLM settings from your shell environment.
It does not require separate `STOCK_AGENT_*` API variables.

```bash
python3 -m dailyinsight.cli run \
  --input examples/sample_brief.json \
  --output reports \
  --mode live
```

Environment variables:

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | live only | API key |
| `ANTHROPIC_BASE_URL` | no | Anthropic-compatible base URL |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | no | Default fast GLM model |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | no | Fallback model |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | no | Fallback model |
| `STOCK_AGENT_TIMEOUT` | no | Timeout seconds |
| `STOCK_AGENT_MAX_TOKENS` | no | Max output tokens |

## Input Schema

See [`examples/sample_brief.json`](/Users/pf/workspace/stock/examples/sample_brief.json).

Main sections:

- `date`
- `world_market`
- `headlines`
- `watchlist`
- `notes`
- `candidate_universe`

## Output

The report is markdown-first and designed to exceed the baseline in [`STOCK.md`](/Users/pf/workspace/stock/STOCK.md):

- top decision dashboard
- source validation table with URLs
- world-market regime summary
- scouting table
- price/range dashboard
- domain / competition / risk / debate / reflection sections
- probability and future-view reasoning
- ASCII conviction/risk/price/scenario/action charts
- explicit buy/sell execution framing

## Verification

Run:

```bash
python3 -m unittest discover -s tests
```
# stock
