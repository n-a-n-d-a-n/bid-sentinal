"""
Verification Cache Manager.

Caches verification responses with status tags: LIVE, CACHED, STALE.
Never treats stale cached results as live verifications.
"""
import time
import structlog
from typing import Optional, Dict, Any, Tuple

logger = structlog.get_logger(__name__)

class VerificationCacheManager:
    def __init__(self, ttl_seconds: float = 3600.0):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[Dict[str, Any], float]] = {}

    def _make_key(self, provider: str, identifier: str) -> str:
        return f"{provider.upper()}:{identifier.strip().upper()}"

    def get(self, provider: str, identifier: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Returns: (cached_data, cache_status)
        cache_status values: LIVE | CACHED | STALE | MISS
        """
        key = self._make_key(provider, identifier)
        if key not in self._cache:
            return None, "MISS"

        data, timestamp = self._cache[key]
        age = time.time() - timestamp

        if age <= self.ttl_seconds:
            return data, "CACHED"
        else:
            return data, "STALE"

    def put(self, provider: str, identifier: str, data: Dict[str, Any]):
        key = self._make_key(provider, identifier)
        self._cache[key] = (data, time.time())

verification_cache = VerificationCacheManager()
