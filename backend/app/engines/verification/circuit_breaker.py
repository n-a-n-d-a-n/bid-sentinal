"""
Circuit Breaker for Government API Adapters.

States:
- CLOSED: Normal operation, requests pass through.
- OPEN: Provider has repeatedly failed. Requests immediately return UNAVAILABLE.
- HALF_OPEN: Cooldown expired. Probe test request allowed to check recovery.
"""
import time
import structlog
from typing import Dict, Any

logger = structlog.get_logger(__name__)

class CircuitBreakerState:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class ProviderCircuitBreaker:
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 30.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self._states: Dict[str, str] = {}
        self._failure_counts: Dict[str, int] = {}
        self._last_failure_times: Dict[str, float] = {}

    def get_state(self, provider_name: str) -> str:
        state = self._states.get(provider_name, CircuitBreakerState.CLOSED)
        if state == CircuitBreakerState.OPEN:
            last_fail = self._last_failure_times.get(provider_name, 0.0)
            if time.time() - last_fail >= self.cooldown_seconds:
                logger.info("circuit_breaker_half_open", provider=provider_name)
                self._states[provider_name] = CircuitBreakerState.HALF_OPEN
                return CircuitBreakerState.HALF_OPEN
        return state

    def record_success(self, provider_name: str):
        self._failure_counts[provider_name] = 0
        self._states[provider_name] = CircuitBreakerState.CLOSED

    def record_failure(self, provider_name: str):
        count = self._failure_counts.get(provider_name, 0) + 1
        self._failure_counts[provider_name] = count
        self._last_failure_times[provider_name] = time.time()

        if count >= self.failure_threshold:
            logger.warning("circuit_breaker_opened", provider=provider_name, failures=count)
            self._states[provider_name] = CircuitBreakerState.OPEN

circuit_breaker = ProviderCircuitBreaker()
