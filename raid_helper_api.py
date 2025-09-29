"""Fetch + model raid events from Raid Helper API."""
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import pytz
from config import RAID_HELPER_BASE_URL, API_TIMEOUT
from utils import get_timezone, safe_api_call, safe_int_conversion


@dataclass
class RaidEvent:
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
    timezone_name: str = None

    def get_datetime_in_timezone(self, timezone_name: str = None) -> datetime:
        utc_dt = datetime.fromtimestamp(self.unix_time, tz=pytz.UTC)
        return utc_dt.astimezone(get_timezone(timezone_name or self.timezone_name))

    @property
    def datetime_local(self) -> datetime:
        return self.get_datetime_in_timezone()


class RaidHelperAPI:
    """Client for interacting with Raid Helper API."""
    
    def __init__(self, access_token: str, timezone_name: str = None):
        self.access_token = access_token
        self.timezone_name = timezone_name
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
                
            server_name = server_data.get('servername', 'Unknown Server')
            events = server_data.get('events', [])
            
            for event_data in events:
                try:
                    event = RaidEvent(
                        title=event_data.get('title'),
                        display_title=event_data.get('displayTitle'),
                        date=event_data.get('date'),
                        time=event_data.get('time'),
                        unix_time=safe_int_conversion(event_data.get('unixtime', 0)),
                        leader=event_data.get('leader'),
                        description=event_data.get('description'),
                        server_name=server_name,
                        server_id=event_data.get('serverId', server_id),
                        signup_count=event_data.get('signupcount', '0'),
                        channel_name=event_data.get('channelName'),
                        image=event_data.get('image'),
                        color=event_data.get('color', '255,0,0'),
                        timezone_name=self.timezone_name
                    )
                    all_events.append(event)
                except (ValueError, TypeError) as e:
                    print(f"Error parsing event from server {server_name}: {e}")
                    continue
        
        # Sort events by datetime
        all_events.sort(key=lambda x: x.unix_time)
        return all_events