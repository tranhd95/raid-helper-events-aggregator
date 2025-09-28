"""
Raid Helper API client for fetching events from multiple Discord servers.
"""
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import pytz
from config import RAID_HELPER_BASE_URL, API_TIMEOUT
from utils import get_timezone, safe_api_call, safe_int_conversion, format_czech_date, safe_get_dict_value


@dataclass
class RaidEvent:
    """Represents a single raid event."""
    title: str
    display_title: str
    date: str
    time: str
    unix_time: int
    leader: str
    description: str
    server_name: str
    server_id: str
    signup_count: str
    channel_name: str
    image: str
    color: str
    
    @property
    def datetime_cz(self) -> datetime:
        """Get the event datetime in Czech timezone."""
        utc_dt = datetime.fromtimestamp(self.unix_time, tz=pytz.UTC)
        cz_tz = get_timezone()
        return utc_dt.astimezone(cz_tz)
    
    @property
    def date_formatted_cz(self) -> str:
        """Get Czech formatted date (e.g., 'Po 23.9.2025')."""
        return format_czech_date(self.datetime_cz)


class RaidHelperAPI:
    """Client for interacting with Raid Helper API."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'RaidHelperCalendar/1.0'
        })
    
    def fetch_server_events(self, server_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch events for a single server.
        
        Args:
            server_id: Discord server ID
            
        Returns:
            Server data including events, or None if request fails
        """
        def _make_request():
            payload = {
                "serverid": server_id,
                "accessToken": self.access_token
            }
            
            response = self.session.post(RAID_HELPER_BASE_URL, json=payload, timeout=API_TIMEOUT)
            response.raise_for_status()
            return response.json()
        
        result = safe_api_call(_make_request)
        if result is None:
            print(f"Error fetching events for server {server_id}")
        return result
    
    def fetch_all_events(self, server_ids: List[str]) -> List[RaidEvent]:
        """
        Fetch events from multiple servers and return as RaidEvent objects.
        
        Args:
            server_ids: List of Discord server IDs
            
        Returns:
            List of RaidEvent objects
        """
        all_events = []
        
        for server_id in server_ids:
            server_data = self.fetch_server_events(server_id)
            
            if not server_data:
                continue
                
            server_name = safe_get_dict_value(server_data, 'servername', 'Unknown Server')
            events = safe_get_dict_value(server_data, 'events', [])
            
            for event_data in events:
                try:
                    event = RaidEvent(
                        title=safe_get_dict_value(event_data, 'title'),
                        display_title=safe_get_dict_value(event_data, 'displayTitle'),
                        date=safe_get_dict_value(event_data, 'date'),
                        time=safe_get_dict_value(event_data, 'time'),
                        unix_time=safe_int_conversion(event_data.get('unixtime', 0)),
                        leader=safe_get_dict_value(event_data, 'leader'),
                        description=safe_get_dict_value(event_data, 'description'),
                        server_name=server_name,
                        server_id=safe_get_dict_value(event_data, 'serverId', server_id),
                        signup_count=safe_get_dict_value(event_data, 'signupcount', '0'),
                        channel_name=safe_get_dict_value(event_data, 'channelName'),
                        image=safe_get_dict_value(event_data, 'image'),
                        color=safe_get_dict_value(event_data, 'color', '255,0,0')
                    )
                    all_events.append(event)
                except (ValueError, TypeError) as e:
                    print(f"Error parsing event from server {server_name}: {e}")
                    continue
        
        # Sort events by datetime
        all_events.sort(key=lambda x: x.unix_time)
        return all_events