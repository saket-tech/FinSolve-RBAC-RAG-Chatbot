"""Token usage tracking and cost estimation with console alerts."""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

# Groq Llama-3.3-70B pricing (USD per 1M tokens as of 2024)
_COST_PER_1M_INPUT = 0.59
_COST_PER_1M_OUTPUT = 0.79

# Alert threshold in USD — warn if session total exceeds this
COST_ALERT_THRESHOLD_USD = 1.0


@dataclass
class UsageRecord:
    timestamp: str
    username: str
    role: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float


class CostTracker:
    """Thread-safe token usage and cost tracker."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._records: list[UsageRecord] = []
        self._session_cost: float = 0.0

    def record(
        self,
        username: str,
        role: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> UsageRecord:
        cost = (
            prompt_tokens / 1_000_000 * _COST_PER_1M_INPUT
            + completion_tokens / 1_000_000 * _COST_PER_1M_OUTPUT
        )
        record = UsageRecord(
            timestamp=datetime.utcnow().isoformat(),
            username=username,
            role=role,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost_usd=round(cost, 6),
        )
        with self._lock:
            self._records.append(record)
            self._session_cost += cost

        logger.info(
            "TOKEN_USAGE user=%s role=%s model=%s prompt=%d completion=%d cost=$%.6f",
            username, role, model, prompt_tokens, completion_tokens, cost,
        )

        # Console alert if threshold exceeded
        if self._session_cost >= COST_ALERT_THRESHOLD_USD:
            logger.warning(
                "COST_ALERT: Session total $%.4f has exceeded threshold of $%.2f",
                self._session_cost,
                COST_ALERT_THRESHOLD_USD,
            )

        return record

    def summary(self) -> dict:
        with self._lock:
            total_prompt = sum(r.prompt_tokens for r in self._records)
            total_completion = sum(r.completion_tokens for r in self._records)
            return {
                "total_requests": len(self._records),
                "total_prompt_tokens": total_prompt,
                "total_completion_tokens": total_completion,
                "total_tokens": total_prompt + total_completion,
                "estimated_total_cost_usd": round(self._session_cost, 4),
            }

    def get_records(self) -> list[UsageRecord]:
        with self._lock:
            return list(self._records)


# Global singleton
_tracker = CostTracker()


def get_tracker() -> CostTracker:
    return _tracker
