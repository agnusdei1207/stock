from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class SourceRegistry:
    preferred_domains: dict[str, str]
    routing_domains: dict[str, str]
    blocked_domains: dict[str, str]

    @classmethod
    def load(cls, path: str) -> "SourceRegistry":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            preferred_domains=payload.get("preferred_domains", {}),
            routing_domains=payload.get("routing_domains", {}),
            blocked_domains=payload.get("blocked_domains", {}),
        )

    def classify(self, url: str) -> tuple[str, str]:
        hostname = urlparse(url).netloc.lower().replace("www.", "")
        if hostname in self.blocked_domains:
            return "blocked", self.blocked_domains[hostname]
        if hostname in self.preferred_domains:
            return "preferred", self.preferred_domains[hostname]
        if hostname in self.routing_domains:
            return "routing", self.routing_domains[hostname]
        return "unknown", "not in registry"
