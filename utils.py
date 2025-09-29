"""Utility helpers for Raid Helper Calendar (kept intentionally lean)."""
import requests
from typing import Optional, Callable, Any
from datetime import datetime
import pytz
from config import DEFAULT_TIMEZONE


def get_timezone(timezone_name: str = None) -> pytz.BaseTzInfo:
    """Return pytz timezone; fall back to default if name invalid."""
    if timezone_name is None:
        timezone_name = DEFAULT_TIMEZONE
    
    try:
        return pytz.timezone(timezone_name)
    except pytz.exceptions.UnknownTimeZoneError:
        return pytz.timezone(DEFAULT_TIMEZONE)


def safe_api_call(func: Callable, *args, **kwargs) -> Optional[Any]:
    """Execute an API call; swallow request + generic exceptions, return None on failure."""
    try:
        return func(*args, **kwargs)
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def safe_int_conversion(value: Any, default: int = 0) -> int:
    """Convert to int or return default if it fails."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


## Removed date formatting helpers (handled inline where needed).