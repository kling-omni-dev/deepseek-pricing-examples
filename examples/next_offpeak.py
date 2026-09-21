"""Report the current DeepSeek billing window and when it changes.

Peak: 01:00-04:00 and 06:00-10:00 UTC, Monday to Friday (per deepseek.ai and
CostGoat). Everything else, including weekends, is off-peak at half price.

Usage:
    python3 examples/next_offpeak.py
"""
from datetime import datetime, timedelta, timezone

from pricing import is_peak


def next_change(start: datetime) -> datetime:
    """Walk forward minute by minute until the peak/off-peak state flips."""
    state = is_peak(start)
    t = start.replace(second=0, microsecond=0)
    limit = t + timedelta(days=8)  # a full week always contains a flip
    while t < limit:
        t += timedelta(minutes=1)
        if is_peak(t) != state:
            return t
    raise RuntimeError('no window change found within 8 days')


def main() -> int:
    now = datetime.now(timezone.utc)
    flip = next_change(now)
    wait = flip - now
    hours = wait.total_seconds() / 3600
    if is_peak(now):
        print(f'now: PEAK (double rate). Off-peak resumes at {flip:%a %Y-%m-%d %H:%M} UTC, in {hours:.1f} h.')
        print('hold batch jobs until then.')
    else:
        print(f'now: off-peak. Next peak window starts at {flip:%a %Y-%m-%d %H:%M} UTC, in {hours:.1f} h.')
        print('jobs that finish before then run at half price.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
