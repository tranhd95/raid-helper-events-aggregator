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


def get_server_ids() -> List[str]:
    """Get server IDs from the default configuration."""
    return DEFAULT_SERVER_IDS


@st.cache_data(ttl=CACHE_TTL)  # Cache for 1 hour
def fetch_and_process_events(access_token: str, server_ids: List[str]) -> Dict:
    """Fetch and process events with caching."""
    api = RaidHelperAPI(access_token)
    all_events = api.fetch_all_events(server_ids)
    
    if not all_events:
        return None
    
    processor = EventProcessor()
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
    """Render a single event as a simple markdown list item."""
    # Create basic markdown list item
    event_info = f"#### {event.display_title}"
    event_info += f"\n  - at **{event.time}** with **{event.server_name}**"
    event_info += f"\n  - Signed up: **{event.signup_count}**"
    
    if event.channel_name:
        event_info += f"\n  - Channel: #{event.channel_name}"
    
    if event.description.strip():
        event_info += f"\n  --- \n{event.description}"
        
        st.error(event_info)


def render_events_by_day(events_by_day: Dict[str, List[RaidEvent]], title: str):
    """Render events grouped by day using columns."""
    if not events_by_day:
        st.info("No events")
        return
    
    if title:
        st.subheader(title)
    
    # Create columns for each day
    days = list(events_by_day.keys())
    if len(days) == 1:
        # If only one day, use full width
        col = st.columns(1, border=True)[0]
        with col:
            day = days[0]
            events = events_by_day[day]
            st.markdown(f"### {day}")
            for event in events:
                render_event_card(event)
    else:
        # Create columns for multiple days
        cols = st.columns(len(days), border=True)
        for i, (day, events) in enumerate(events_by_day.items()):
            with cols[i]:
                st.markdown(f"### {day}")
                for event in events:
                    render_event_card(event)


def main():
    st.set_page_config(
        page_title="Raid Helper Calendar",
        page_icon="🗡️",
        layout="wide"
    )
    
    st.title("🗡️ Raid Helper Calendar")
    st.markdown("Raid event aggregator from multiple Discord servers")
    
    # Get access token from configuration
    access_token = get_access_token()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
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
            events_data = fetch_and_process_events(access_token, server_ids)
            
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
    processor = EventProcessor()
    
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
