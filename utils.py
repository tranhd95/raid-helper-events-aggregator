"""
Common utility functions for the Raid Helper Calendar application.
"""
import requests
from typing import Optional, Callable, Any
from datetime import datetime
import pytz
from config import TIMEZONE, CZECH_DAYS


def get_timezone() -> pytz.BaseTzInfo:
    """Get the configured timezone object."""
    return pytz.timezone(TIMEZONE)


def safe_api_call(func: Callable, *args, **kwargs) -> Optional[Any]:
    """
    Safely execute an API call with error handling.
    
    Args:
        func: Function to call
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Function result or None if error occurs
    """
    try:
        return func(*args, **kwargs)
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def safe_int_conversion(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer with fallback.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def format_czech_date(dt: datetime) -> str:
    """
    Format datetime to Czech date string (e.g., 'Po 23.9.2025').
    
    Args:
        dt: Datetime object in Czech timezone
        
    Returns:
        Formatted date string
    """
    day_name = CZECH_DAYS[dt.weekday()]
    return f"{day_name} {dt.day}.{dt.month}.{dt.year}"


def parse_czech_date(czech_date_str: str, tz: pytz.BaseTzInfo) -> datetime:
    """
    Parse Czech date string back to datetime for sorting.
    
    Args:
        czech_date_str: String like 'Po 23.9.2025'
        tz: Timezone to use for the result
        
    Returns:
        datetime object
    """
    try:
        # Extract the date part (remove day name)
        date_part = czech_date_str.split(' ', 1)[1]  # '23.9.2025'
        day, month, year = map(int, date_part.split('.'))
        return datetime(year, month, day, tzinfo=tz)
    except (ValueError, IndexError):
        # Fallback to current time if parsing fails
        return datetime.now(tz)


def safe_get_dict_value(data: dict, key: str, default: Any = '') -> Any:
    """
    Safely get value from dictionary with default fallback.
    
    Args:
        data: Dictionary to get value from
        key: Key to look for
        default: Default value if key not found
        
    Returns:
        Value from dictionary or default
    """
    return data.get(key, default)