"""Minimal event grouping + categorization helpers."""
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from raid_helper_api import RaidEvent
from utils import get_timezone


class EventProcessor:
    def __init__(self, timezone_name: str = None):
        self.local_tz = get_timezone(timezone_name)

    # --- period bounds -------------------------------------------------
    def _now(self) -> datetime:
        return datetime.now(self.local_tz)

    def _week_bounds(self, base: datetime) -> Tuple[datetime, datetime]:
        monday = base.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=base.weekday())
        sunday = monday + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return monday, sunday

    def _yesterday_to_week_end(self) -> Tuple[datetime, datetime]:
        now_local = self._now()
        yesterday_start = (now_local - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        _, week_end = self._week_bounds(now_local)
        return yesterday_start, week_end

    def _next_week_bounds(self) -> Tuple[datetime, datetime]:
        current_start, _ = self._week_bounds(self._now())
        next_monday = current_start + timedelta(days=7)
        return self._week_bounds(next_monday)

    # --- categorization ------------------------------------------------
    def categorize_events_with_next_week(self, events: List[RaidEvent]) -> Dict[str, List[RaidEvent]]:
        """Return events split into: this_period (yesterday..Sun), next_week, other."""
        period_start, period_end = self._yesterday_to_week_end()
        next_start, next_end = self._next_week_bounds()
        buckets = {"this_period": [], "next_week": [], "other": []}
        for e in events:
            dt = e.datetime_local
            if period_start <= dt <= period_end:
                buckets["this_period"].append(e)
            elif next_start <= dt <= next_end:
                buckets["next_week"].append(e)
            else:
                buckets["other"].append(e)
        return buckets

    # --- grouping ------------------------------------------------------
    def group_events_by_day(self, events: List[RaidEvent]) -> Dict[datetime, List[RaidEvent]]:
        grouped = defaultdict(list)
        for e in events:
            grouped[e.datetime_local.date()].append(e)
        # sort each day's events
        for day_events in grouped.values():
            day_events.sort(key=lambda x: x.unix_time)
        # return ordered by date
        return dict(sorted(grouped.items(), key=lambda kv: kv[0]))