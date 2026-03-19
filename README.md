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

The live mode follows the same Anthropic-compatible GLM direction used in `../Pentesting`.
Default target model is `glm-5`.
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
| `ANTHROPIC_API_KEY` | preferred | API key |
| `PENTEST_API_KEY` | fallback | Reuse pentesting key if present |
| `ANTHROPIC_BASE_URL` | preferred | Anthropic-compatible base URL |
| `PENTEST_BASE_URL` | fallback | Reuse pentesting base URL if present |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | preferred | Defaults well to `glm-5` in your shell |
| `PENTEST_MODEL` | fallback | Reuse pentesting model if present |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | fallback | Secondary fallback |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | fallback | Secondary fallback |
| `STOCK_AGENT_TIMEOUT` | no | Timeout seconds |
| `STOCK_AGENT_MAX_TOKENS` | no | Max output tokens |

Resolution order:

1. API key: `ANTHROPIC_API_KEY` -> `PENTEST_API_KEY`
2. Base URL: `ANTHROPIC_BASE_URL` -> `PENTEST_BASE_URL` -> `https://api.z.ai/api/anthropic`
3. Model: `ANTHROPIC_DEFAULT_OPUS_MODEL` -> `PENTEST_MODEL` -> `ANTHROPIC_DEFAULT_SONNET_MODEL` -> `ANTHROPIC_DEFAULT_HAIKU_MODEL` -> `glm-5`

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
