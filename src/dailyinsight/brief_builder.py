from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .source_registry import SourceRegistry


def _normalize_headline(item: dict, registry: SourceRegistry) -> dict:
    status, note = registry.classify(item.get("url", ""))
    source = item.get("source", "Unknown")
    return {
        "source": source,
        "url": item.get("url", ""),
        "headline": item.get("headline", ""),
        "why_it_matters": item.get("why_it_matters", ""),
        "source_status": status,
        "source_note": note,
    }


def build_brief_from_raw(
    raw_path: str,
    registry_path: str,
    output_path: str,
    *,
    watchlist: list[str] | None = None,
    notes: list[str] | None = None,
    candidate_universe: list[dict] | None = None,
    world_market: dict | None = None,
) -> str:
    raw_payload = json.loads(Path(raw_path).read_text(encoding="utf-8"))
    registry = SourceRegistry.load(registry_path)

    normalized = [_normalize_headline(item, registry) for item in raw_payload.get("headlines", [])]
    filtered = [item for item in normalized if item["source_status"] != "blocked"]

    payload = {
        "date": raw_payload.get("date", date.today().isoformat()),
        "world_market": world_market or raw_payload.get("world_market", {}),
        "headlines": filtered,
        "watchlist": watchlist or raw_payload.get("watchlist", []),
        "notes": notes or raw_payload.get("notes", []),
        "candidate_universe": candidate_universe or raw_payload.get("candidate_universe", []),
    }

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(target)
