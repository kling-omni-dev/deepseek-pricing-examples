"""DeepSeek API rates per 1M tokens (USD) and a per-call cost estimator.

Source: https://api-docs.deepseek.com/quick_start/pricing (snapshot 2026-09).
Peak hours per deepseek.ai and CostGoat: 01:00-04:00 and 06:00-10:00 UTC,
Monday to Friday. Re-check the official page before budgeting.
"""
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Rate:
    cache_hit: float   # input tokens whose prefix was cached
    cache_miss: float  # input tokens not cached
    output: float


# (model, peak) -> per-1M-token rates
RATES = {
    ('deepseek-flash', False): Rate(0.003, 0.15, 0.60),
    ('deepseek-flash', True): Rate(0.006, 0.30, 1.20),
    ('deepseek-v4-pro', False): Rate(0.022, 0.66, 1.98),
    ('deepseek-v4-pro', True): Rate(0.044, 1.32, 3.96),
}
PEAK_WINDOWS = ((1, 4), (6, 10))  # [start, end) hours, UTC, weekdays only


def is_peak(at: datetime) -> bool:
    at = at.astimezone(timezone.utc)
    if at.weekday() >= 5:  # Saturday, Sunday
        return False
    return any(start <= at.hour < end for start, end in PEAK_WINDOWS)


def estimate(model: str, input_tokens: int, output_tokens: int,
             cache_hit_ratio: float = 0.0, at: datetime | None = None) -> float:
    """Return the USD cost of one call."""
    at = at or datetime.now(timezone.utc)
    rate = RATES[(model, is_peak(at))]
    hit = input_tokens * cache_hit_ratio
    miss = input_tokens - hit
    per_m = 1_000_000
    return (hit * rate.cache_hit + miss * rate.cache_miss + output_tokens * rate.output) / per_m


if __name__ == '__main__':
    offpeak = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)  # Monday noon UTC
    peak = datetime(2026, 9, 21, 7, 0, tzinfo=timezone.utc)      # Monday 07:00 UTC
    for label, when in (('off-peak', offpeak), ('peak', peak)):
        for model in ('deepseek-flash', 'deepseek-v4-pro'):
            cost = estimate(model, 100_000, 5_000, cache_hit_ratio=0.5, at=when)
            print(f'{model:16s} {label:9s} 100K in (50% cached) + 5K out = ${cost:.4f}')
