"""API client for M3U Editor."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiohttp import ClientError, ClientSession
from aiohttp.hdrs import METH_GET, METH_POST, METH_PATCH

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEFAULT_TIMEOUT,
    API_ENDPOINT_PLAYLISTS,
    API_ENDPOINT_EPGS,
    API_ENDPOINT_CHANNELS,
    API_ENDPOINT_PROXY_STATUS,
    API_ENDPOINT_PROXY_STREAMS,
    API_ENDPOINT_PLAYLIST_STATS,
    API_ENDPOINT_PLAYLIST_SYNC,
    API_ENDPOINT_EPG_SYNC,
    API_ENDPOINT_TOKEN,
    API_ENDPOINT_TOKEN_REFRESH,
)

_LOGGER = logging.getLogger(__name__)


class M3UEditorAPI:
    """API client for M3U Editor."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize the API client."""
        self.hass = hass
        self._config = config
        self._session: ClientSession | None = None
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._token_expiry: float | None = None
        self._base_url: str = self._build_base_url()

    def _build_base_url(self) -> str:
        """Build the base URL from config."""
        protocol = self._config.get(CONF_PROTOCOL, "http")
        host = self._config.get(CONF_HOST, "localhost")
        port = self._config.get(CONF_PORT, 36400)
        return f"{protocol}://{host}:{port}"

    async def async_get_session(self) -> ClientSession:
        """Get or create a session."""
        if self._session is None or self._session.closed:
            self._session = async_get_clientsession(self.hass)
        return self._session

    async def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token."""
        if self._access_token and self._token_expiry and self._token_expiry > asyncio.get_event_loop().time():
            return

        # Try to refresh token if we have one
        if self._refresh_token:
            try:
                await self._refresh_access_token()
                return
            except Exception as err:
                _LOGGER.warning("Failed to refresh token: %s", err)
                self._access_token = None
                self._refresh_token = None

        # Try to authenticate with username/password
        username = self._config.get(CONF_USERNAME)
        password = self._config.get(CONF_PASSWORD)
        
        if username and password:
            try:
                await self._authenticate_with_credentials(username, password)
                return
            except Exception as err:
                _LOGGER.warning("Failed to authenticate with credentials: %s", err)

        # If we have an API key, use it directly
        api_key = self._config.get(CONF_API_KEY)
        if api_key:
            self._access_token = api_key
            # API keys don't expire (or have long expiry)
            self._token_expiry = asyncio.get_event_loop().time() + 86400  # 24 hours

    async def _authenticate_with_credentials(self, username: str, password: str) -> None:
        """Authenticate with username and password."""
        session = await self.async_get_session()
        url = f"{self._base_url}{API_ENDPOINT_TOKEN}"
        
        ssl = self._config.get(CONF_SSL, False)
        verify_ssl = self._config.get(CONF_VERIFY_SSL, True)
        
        data = {
            "username": username,
            "password": password,
        }
        
        async with session.post(
            url,
            json=data,
            ssl=verify_ssl if ssl else False,
            timeout=DEFAULT_TIMEOUT,
        ) as response:
            if response.status == 200:
                auth_data = await response.json()
                self._access_token = auth_data.get("access")
                self._refresh_token = auth_data.get("refresh")
                # Set expiry to 1 hour (token TTL)
                self._token_expiry = asyncio.get_event_loop().time() + 3600
            else:
                raise ClientError(f"Authentication failed: {response.status}")

    async def _refresh_access_token(self) -> None:
        """Refresh the access token."""
        if not self._refresh_token:
            raise ClientError("No refresh token available")

        session = await self.async_get_session()
        url = f"{self._base_url}{API_ENDPOINT_TOKEN_REFRESH}"
        
        ssl = self._config.get(CONF_SSL, False)
        verify_ssl = self._config.get(CONF_VERIFY_SSL, True)
        
        data = {
            "refresh": self._refresh_token,
        }
        
        async with session.post(
            url,
            json=data,
            ssl=verify_ssl if ssl else False,
            timeout=DEFAULT_TIMEOUT,
        ) as response:
            if response.status == 200:
                auth_data = await response.json()
                self._access_token = auth_data.get("access")
                self._refresh_token = auth_data.get("refresh", self._refresh_token)
                # Set expiry to 1 hour (token TTL)
                self._token_expiry = asyncio.get_event_loop().time() + 3600
            else:
                raise ClientError(f"Token refresh failed: {response.status}")

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        
        return headers

    async def async_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> Any:
        """Make an API request."""
        await self._ensure_authenticated()
        
        session = await self.async_get_session()
        url = f"{self._base_url}{endpoint}"
        
        ssl = self._config.get(CONF_SSL, False)
        verify_ssl = self._config.get(CONF_VERIFY_SSL, True)
        headers = self._get_headers()
        
        try:
            async with session.request(
                method,
                url,
                params=params,
                data=data,
                json=json_data,
                headers=headers,
                ssl=verify_ssl if ssl else False,
                timeout=DEFAULT_TIMEOUT,
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    # Token might have expired, try to refresh and retry
                    await self._ensure_authenticated()
                    headers = self._get_headers()
                    async with session.request(
                        method,
                        url,
                        params=params,
                        data=data,
                        json=json_data,
                        headers=headers,
                        ssl=verify_ssl if ssl else False,
                        timeout=DEFAULT_TIMEOUT,
                    ) as retry_response:
                        if retry_response.status == 200:
                            return await retry_response.json()
                        else:
                            raise ClientError(f"API request failed: {retry_response.status}")
                else:
                    raise ClientError(f"API request failed: {response.status}")
        
        except ClientError as err:
            _LOGGER.error("API request error: %s", err)
            raise

    async def async_get_playlists(self) -> list[dict[str, Any]]:
        """Get all playlists."""
        return await self.async_request(METH_GET, API_ENDPOINT_PLAYLISTS)

    async def async_get_epgs(self) -> list[dict[str, Any]]:
        """Get all EPGs."""
        return await self.async_request(METH_GET, API_ENDPOINT_EPGS)

    async def async_get_channels(self, playlist_id: int | None = None) -> list[dict[str, Any]]:
        """Get all channels."""
        params = {}
        if playlist_id:
            params["playlist_id"] = playlist_id
        return await self.async_request(METH_GET, API_ENDPOINT_CHANNELS, params=params)

    async def async_get_system_stats(self) -> dict[str, Any]:
        """Get global system statistics."""
        # Get total channels by fetching 1 channel and reading meta.total
        response = await self.async_request(METH_GET, API_ENDPOINT_CHANNELS, params={"limit": 1})
        meta = response.get("meta", {})
        total_channels = meta.get("total", 0)
        return {"total_channels": total_channels}

    async def async_get_proxy_status(self) -> dict[str, Any]:
        """Get proxy status."""
        return await self.async_request(METH_GET, API_ENDPOINT_PROXY_STATUS)

    async def async_get_proxy_streams(self) -> dict[str, Any]:
        """Get active proxy streams."""
        return await self.async_request(METH_GET, API_ENDPOINT_PROXY_STREAMS)

    async def async_get_playlist_stats(self, uuid: str) -> dict[str, Any]:
        """Get playlist statistics."""
        return await self.async_request(METH_GET, API_ENDPOINT_PLAYLIST_STATS.format(uuid=uuid))

    async def async_sync_playlist(self, uuid: str) -> dict[str, Any]:
        """Sync a playlist."""
        return await self.async_request(METH_GET, API_ENDPOINT_PLAYLIST_SYNC.format(uuid=uuid))

    async def async_sync_epg(self, uuid: str) -> dict[str, Any]:
        """Sync an EPG."""
        return await self.async_request(METH_GET, API_ENDPOINT_EPG_SYNC.format(uuid=uuid))

    async def async_refresh_playlist(self, uuid: str) -> dict[str, Any]:
        """Refresh a playlist."""
        # This is the same as sync for now
        return await self.async_sync_playlist(uuid)

    async def async_refresh_epg(self, uuid: str) -> dict[str, Any]:
        """Refresh an EPG."""
        # This is the same as sync for now
        return await self.async_sync_epg(uuid)

    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
