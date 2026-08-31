"""
Provider Rate Limiter.

Controls request rates per government provider to prevent API throttling.
"""
import time
import structlog
from typing import Dict, Any

logger = structlog.get_logger(__name__)

# Configurable requests per minute per provider
DEFAULT_RATE_LIMITS = {
    "GST": 60,
    "PAN": 60,
    "MCA": 30,
    "UDYAM": 60,
    "EPFO": 30,
    "ESIC": 30,
    "DIGILOCKER": 60,
    "BIS": 30,
    "GEM": 60,
    "BLACKLIST": 120,
}

class ProviderRateLimiter:
    def __init__(self):
        self._request_history: Dict[str, list] = {}

    def is_allowed(self, provider_name: str) -> bool:
        limit = DEFAULT_RATE_LIMITS.get(provider_name.upper(), 60)
        now = time.time()
        history = self._request_history.get(provider_name, [])

        # Remove requests older than 60 seconds
        history = [t for t in history if now - t < 60.0]
        self._request_history[provider_name] = history

        if len(history) >= limit:
            logger.warning("rate_limit_exceeded", provider=provider_name, limit=limit)
            return False

        history.append(now)
        return True

rate_limiter = ProviderRateLimiter()
