# 🗡️ Raid Helper Calendar

A calendar aggregator for raid events from multiple Discord servers using the Raid Helper API. Displays events grouped by days with localized date and time formatting.

## Features

- ✅ Aggregate events from multiple Discord servers
- ✅ Localized date and time formatting
- ✅ Events grouped by day
- ✅ Current week prominently displayed
- ✅ Next week collapsible section
- ✅ Streamlit web interface
- ✅ Simple server ID management
- ✅ Secure access token input
- ✅ Event caching for better performance

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd raid-helper-calendar
```

2. Install dependencies:
```bash
pip install -e .
```

3. Run the application:
```bash
streamlit run main.py
```

## Usage

### 1. Getting an Access Token

1. Log in to [raid-helper.dev](https://raid-helper.dev)
2. Open Developer Tools (F12)
3. Go to the Network tab
4. Load a page with events
5. Find the request to `/api/events/`
6. Copy the `accessToken` from the request payload

### 2. Setting Up Server IDs

1. In the application sidebar, you can add/remove Discord Server IDs
2. Default server IDs can be edited in `config.py` in the `DEFAULT_SERVER_IDS` variable

### 3. Loading Events

1. Enter your Access Token
2. Check/modify Server IDs
3. Click "🔄 Load Events"

## Project Structure

```
├── main.py              # Main Streamlit application
├── raid_helper_api.py   # API client for Raid Helper
├── event_processor.py   # Event processing and grouping logic
├── config.py           # Configuration settings
├── utils.py            # Utility functions
├── pyproject.toml      # Python project configuration
└── README.md           # This documentation
```

## Requirements

- Python >= 3.12
- Streamlit >= 1.28.0
- Requests >= 2.31.0
- pytz >= 2023.3

## API

The application uses the official Raid Helper API:
- Endpoint: `https://raid-helper.dev/api/events/`
- Payload: `{"serverid": "...", "accessToken": "..."}`

## License

MIT License