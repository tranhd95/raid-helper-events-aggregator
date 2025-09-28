"""
Data processing utilities for grouping and filtering raid events.
"""
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from raid_helper_api import RaidEvent
from utils import get_timezone, parse_czech_date


class EventProcessor:
    """Processes and organizes raid events."""
    
    def __init__(self):
        self.cz_tz = get_timezone()
    
    def get_current_week_bounds(self) -> Tuple[datetime, datetime]:
        """
        Get the start and end of the current week (Monday to Sunday) in Czech timezone.
        
        Returns:
            Tuple of (week_start, week_end) datetime objects
        """
        now_cz = datetime.now(self.cz_tz)
        
        # Get Monday of current week
        days_since_monday = now_cz.weekday()
        week_start = now_cz.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
        
        # Get Sunday of current week
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        return week_start, week_end
    
    def get_next_week_bounds(self) -> Tuple[datetime, datetime]:
        """
        Get the start and end of the next week (Monday to Sunday) in Czech timezone.
        
        Returns:
            Tuple of (week_start, week_end) datetime objects
        """
        current_start, _ = self.get_current_week_bounds()
        
        next_week_start = current_start + timedelta(days=7)
        next_week_end = next_week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        return next_week_start, next_week_end
    
    def get_yesterday_to_week_end_bounds(self) -> Tuple[datetime, datetime]:
        """
        Get the bounds from yesterday to the end of the current week (Sunday) in Czech timezone.
        
        Returns:
            Tuple of (yesterday_start, week_end) datetime objects
        """
        now_cz = datetime.now(self.cz_tz)
        
        # Get yesterday start (00:00:00)
        yesterday_start = (now_cz - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get end of current week (Sunday 23:59:59)
        days_since_monday = now_cz.weekday()
        week_start = now_cz.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        return yesterday_start, week_end
    
    def categorize_events(self, events: List[RaidEvent]) -> Dict[str, List[RaidEvent]]:
        """
        Categorize events into current week, next week, and other.
        
        Args:
            events: List of RaidEvent objects
            
        Returns:
            Dictionary with 'current_week', 'next_week', and 'other' keys
        """
        current_start, current_end = self.get_current_week_bounds()
        next_start, next_end = self.get_next_week_bounds()
        
        categorized = {
            'current_week': [],
            'next_week': [],
            'other': []
        }
        
        for event in events:
            event_dt = event.datetime_cz
            
            if current_start <= event_dt <= current_end:
                categorized['current_week'].append(event)
            elif next_start <= event_dt <= next_end:
                categorized['next_week'].append(event)
            else:
                categorized['other'].append(event)
        
        return categorized
    
    def categorize_events_yesterday_to_week_end(self, events: List[RaidEvent]) -> Dict[str, List[RaidEvent]]:
        """
        Categorize events from yesterday to end of current week.
        
        Args:
            events: List of RaidEvent objects
            
        Returns:
            Dictionary with 'this_period' and 'other' keys
        """
        period_start, period_end = self.get_yesterday_to_week_end_bounds()
        
        categorized = {
            'this_period': [],
            'other': []
        }
        
        for event in events:
            event_dt = event.datetime_cz
            
            if period_start <= event_dt <= period_end:
                categorized['this_period'].append(event)
            else:
                categorized['other'].append(event)
        
        return categorized
    
    def categorize_events_with_next_week(self, events: List[RaidEvent]) -> Dict[str, List[RaidEvent]]:
        """
        Categorize events from yesterday to end of current week, next week, and other.
        
        Args:
            events: List of RaidEvent objects
            
        Returns:
            Dictionary with 'this_period', 'next_week', and 'other' keys
        """
        period_start, period_end = self.get_yesterday_to_week_end_bounds()
        next_start, next_end = self.get_next_week_bounds()
        
        categorized = {
            'this_period': [],
            'next_week': [],
            'other': []
        }
        
        for event in events:
            event_dt = event.datetime_cz
            
            if period_start <= event_dt <= period_end:
                categorized['this_period'].append(event)
            elif next_start <= event_dt <= next_end:
                categorized['next_week'].append(event)
            else:
                categorized['other'].append(event)
        
        return categorized
    
    def group_events_by_day(self, events: List[RaidEvent]) -> Dict[str, List[RaidEvent]]:
        """
        Group events by day with Czech date formatting.
        
        Args:
            events: List of RaidEvent objects
            
        Returns:
            Dictionary with date strings as keys and event lists as values
        """
        grouped = defaultdict(list)
        
        for event in events:
            date_key = event.date_formatted_cz
            grouped[date_key].append(event)
        
        # Sort events within each day by time
        for day_events in grouped.values():
            day_events.sort(key=lambda x: x.unix_time)
        
        # Convert to regular dict and sort by date
        result = dict(grouped)
        sorted_days = sorted(result.keys(), key=lambda day_str: self._parse_czech_date(day_str))
        
        return {day: result[day] for day in sorted_days}
    
    def _parse_czech_date(self, czech_date_str: str) -> datetime:
        """
        Parse Czech date string back to datetime for sorting.
        
        Args:
            czech_date_str: String like 'Po 23.9.2025'
            
        Returns:
            datetime object
        """
        return parse_czech_date(czech_date_str, self.cz_tz)