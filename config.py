"""
Configuration constants for the Raid Helper Calendar application.
"""
import streamlit as st

# Default server IDs - these will be used to fetch initial server information
# You can add/remove server IDs here
DEFAULT_SERVER_IDS = [
    "902588385607163955", 
    "1327632150232698952",
    "1082291130625966110",
    "1135207896100114514",
    "1318284716092428298",
    "1305782557920464896",
    "494289106625626112",
    "1145012794589196539",
    "1146543294818553996",
    "1362492441814499568",
    "1394723327167168563",
    "1388288271632830494"
]

# API Configuration
RAID_HELPER_BASE_URL = "https://raid-helper.dev/api/events/"
API_TIMEOUT = 10

# Application Configuration
CACHE_TTL = 3600  # 1 hour in seconds
DEFAULT_TIMEZONE = 'Europe/Prague'  # Fallback timezone if browser detection fails


def get_access_token() -> str:
    """Get the access token from Streamlit secrets."""
    return st.secrets["access_token"]