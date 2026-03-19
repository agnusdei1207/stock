from __future__ import annotations

import json
from pathlib import Path

from .models import DailyBrief


def load_brief(path: str) -> DailyBrief:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return DailyBrief(
        date=payload["date"],
        world_market=payload.get("world_market", {}),
        headlines=payload.get("headlines", []),
        watchlist=payload.get("watchlist", []),
        notes=payload.get("notes", []),
        candidate_universe=payload.get("candidate_universe", []),
    )
