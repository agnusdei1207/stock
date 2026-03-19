from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    api_key: str | None = None
    base_url: str = "https://api.z.ai/api/anthropic"
    model: str = "glm-5"
    timeout: int = 60
    max_tokens: int = 4000

    @classmethod
    def from_env(cls) -> "AppConfig":
        timeout_raw = os.getenv("STOCK_AGENT_TIMEOUT", "60")
        model = (
            os.getenv("ANTHROPIC_DEFAULT_OPUS_MODEL")
            or os.getenv("PENTEST_MODEL")
            or os.getenv("ANTHROPIC_DEFAULT_SONNET_MODEL")
            or os.getenv("ANTHROPIC_DEFAULT_HAIKU_MODEL")
            or "glm-5"
        )
        return cls(
            api_key=os.getenv("ANTHROPIC_API_KEY") or os.getenv("PENTEST_API_KEY"),
            base_url=(
                os.getenv("ANTHROPIC_BASE_URL")
                or os.getenv("PENTEST_BASE_URL")
                or "https://api.z.ai/api/anthropic"
            ),
            model=model,
            timeout=int(timeout_raw),
            max_tokens=int(os.getenv("STOCK_AGENT_MAX_TOKENS", "4000")),
        )
