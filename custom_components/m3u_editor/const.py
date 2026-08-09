"""Constants for the M3U Editor integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "m3u_editor"

# Default values
DEFAULT_NAME = "M3U Editor"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 36400
DEFAULT_PROTOCOL = "http"
DEFAULT_API_VERSION = "v1"

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_PROTOCOL = "protocol"
CONF_API_KEY = "api_key"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SSL = "ssl"
CONF_VERIFY_SSL = "verify_ssl"
CONF_SCAN_INTERVAL = "scan_interval"

# API endpoints (from web.php)
API_ENDPOINT_PLAYLISTS = "/user/playlists"
API_ENDPOINT_EPGS = "/user/epgs"
API_ENDPOINT_CHANNELS = "/channel/get"
API_ENDPOINT_PLAYLIST_STATS = "/playlist/{uuid}/stats"
API_ENDPOINT_PLAYLIST_SYNC = "/playlist/{uuid}/sync"
API_ENDPOINT_EPG_SYNC = "/epg/{uuid}/sync"

# Token endpoints (Dispatcharr-compatible from api.php)
API_ENDPOINT_TOKEN = "/api/accounts/token"
API_ENDPOINT_TOKEN_REFRESH = "/api/accounts/token/refresh"

# Timeout constants
DEFAULT_TIMEOUT = 30
DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)

# Attributes
ATTR_UUID = "uuid"
ATTR_NAME = "name"
ATTR_TOTAL_CHANNELS = "total_channels"
ATTR_ENABLED_CHANNELS = "enabled_channels"
ATTR_LIVE_CHANNELS = "live_channels"
ATTR_VOD_CHANNELS = "vod_channels"
ATTR_GROUPS_COUNT = "groups_count"
ATTR_PROXY_ENABLED = "proxy_enabled"
ATTR_ACTIVE_STREAMS = "active_streams"
ATTR_CHANNEL_COUNT = "channel_count"
ATTR_LAST_SYNC = "last_sync"
ATTR_STATUS = "status"
ATTR_SOURCE_TYPE = "source_type"
ATTR_IS_PROCESSING = "is_processing"

# Services
SERVICE_SYNC_PLAYLIST = "sync_playlist"
SERVICE_SYNC_EPG = "sync_epg"
SERVICE_REFRESH_DATA = "refresh_data"

# Entity types
ENTITY_TYPE_PLAYLIST = "playlist"
ENTITY_TYPE_CHANNEL = "channel"
ENTITY_TYPE_EPG = "epg"
ENTITY_TYPE_PROXY = "proxy"

# Error codes
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_INVALID_AUTH = "invalid_auth"
ERROR_API_ERROR = "api_error"
