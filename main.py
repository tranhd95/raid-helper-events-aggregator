"""
Raid Helper Calendar Aggregator
A Streamlit app to aggregate raid events from multiple Discord servers using Raid Helper API.
"""
import streamlit as st
from typing import List, Dict
import datetime
from raid_helper_api import RaidHelperAPI, RaidEvent
from event_processor import EventProcessor
from config import DEFAULT_SERVER_IDS, CACHE_TTL, get_access_token
# Removed timezone_detector import - using st.context.timezone instead


def get_server_ids() -> List[str]:
    """Get server IDs from the default configuration."""
    return DEFAULT_SERVER_IDS


@st.cache_data(ttl=CACHE_TTL)  # Cache for 1 hour
def fetch_and_process_events(access_token: str, server_ids: List[str], user_timezone: str) -> Dict:
    """Fetch and process events with caching."""
    api = RaidHelperAPI(access_token, user_timezone)
    all_events = api.fetch_all_events(server_ids)
    
    if not all_events:
        return None
    
    processor = EventProcessor(user_timezone)
    categorized_events = processor.categorize_events_with_next_week(all_events)
    
    return {
        'all_events': all_events,
        'categorized_events': categorized_events,
        'timestamp': datetime.datetime.now()
    }


def get_server_names_from_events(events: List[RaidEvent]) -> List[str]:
    """Get unique server names from the fetched events."""
    seen_names = set()
    server_names = []
    for event in events:
        if event.server_name not in seen_names:
            seen_names.add(event.server_name)
            server_names.append(event.server_name)
    return server_names


def render_event_card(event: RaidEvent):
    formatted_time = event.get_datetime_in_timezone().strftime('%H:%M')
    lines = [
        f"#### {event.display_title}",
        f"**w/ {event.server_name}**",
        f"- at **{formatted_time}**\n\n- Signups: **{event.signup_count}**",
    ]
    if event.channel_name:
        lines.append(f"- #{event.channel_name}")
    desc = (event.description or '').strip()
    if desc:
        lines.append("---")
        lines.append(desc)
    from textwrap import dedent
    st.info(dedent("\n".join(lines)))


def render_events_by_day(events_by_day: Dict, title: str):
    if not events_by_day:
        st.info("No events")
        return
    if title:
        st.subheader(title)
    days = list(events_by_day.keys())
    display_keys = [d.strftime('%a, %b %d') for d in days]
    if len(days) == 1:
        col = st.columns(1, border=True)[0]
        with col:
            st.markdown(f"### {display_keys[0]}")
            for ev in events_by_day[days[0]]:
                render_event_card(ev)
        return
    cols = st.columns(len(days), border=True)
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"### {display_keys[i]}")
            for ev in events_by_day[day]:
                render_event_card(ev)


def main():
    st.set_page_config(
        page_title="Raid Helper Calendar",
        page_icon="🗡️",
        layout="wide"
    )
    
    st.title("🗡️ Raid Helper Calendar")
    st.markdown("Raid event aggregator from multiple Discord servers")
    
    # Get user's timezone from browser using Streamlit's built-in context
    try:
        user_timezone = st.context.timezone
    except (AttributeError, Exception):
        # Fallback for older Streamlit versions or when context is not available
        user_timezone = 'Europe/Prague'
    
    # Get access token from configuration
    access_token = get_access_token()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Show timezone info
        st.markdown("---")
        st.subheader("🌍 Timezone")
        st.info(f"**Detected:** {user_timezone}")
        
        # Show current time in user's timezone
        try:
            import pytz
            from datetime import datetime
            tz = pytz.timezone(user_timezone)
            current_time = datetime.now(tz)
            st.success(f"**Local time:** {current_time.strftime('%H:%M:%S %Z')}")
        except Exception as e:
            st.warning(f"Timezone error: {e}")
        
        # Force refresh button
        if st.button("🔄 Clear cache and refresh", type="primary"):
            st.cache_data.clear()
            st.rerun()
    
    # Get server configuration
    server_ids = get_server_ids()
    
    if not server_ids:
        st.warning("⚠️ Please add at least one Server ID")
        return
    
    # Fetch events using cached function
    with st.spinner("Loading events..."):
        try:
            events_data = fetch_and_process_events(access_token, server_ids, user_timezone)
            
            if not events_data:
                st.error("❌ Failed to load events. Check Access Token and Server IDs.")
                return
            
            all_events = events_data['all_events']
            categorized_events = events_data['categorized_events']
            timestamp = events_data['timestamp']
            
            # Show cache info in sidebar
            with st.sidebar:
                st.markdown("---")
                st.subheader("📊 Cache Status")
                st.success(f"Loaded: {timestamp.strftime('%H:%M:%S')}")
                
                # Show server info
                server_names = get_server_names_from_events(all_events)
                if server_names:
                    for name in server_names:
                        st.markdown(f"- **{name}**")
                
        except Exception as e:
            st.error(f"❌ Error loading events: {str(e)}")
            return
    
    # Display events
    processor = EventProcessor(user_timezone)
    
    # Events from yesterday to end of week
    this_period_events = categorized_events.get('this_period', [])
    if this_period_events:
        this_period_by_day = processor.group_events_by_day(this_period_events)
        render_events_by_day(this_period_by_day, "📅 Yesterday to End of Week")
    
    # Next week events
    next_week_events = categorized_events.get('next_week', [])
    if next_week_events:
        with st.expander(f"📅 Next Week Events ({len(next_week_events)} events)", expanded=False):
            next_week_by_day = processor.group_events_by_day(next_week_events)
            render_events_by_day(next_week_by_day, "")


if __name__ == "__main__":
    main()
