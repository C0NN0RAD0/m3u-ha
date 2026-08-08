"""Services for M3U Editor integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.service import async_register_admin_service

from .const import (
    DOMAIN,
    SERVICE_SYNC_PLAYLIST,
    SERVICE_SYNC_EPG,
    SERVICE_REFRESH_DATA,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up services for M3U Editor integration."""
    _LOGGER.debug("Setting up M3U Editor services")
    
    api_client = hass.data[DOMAIN][entry.entry_id]["api"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    async def sync_playlist_service(call: ServiceCall) -> None:
        """Service to sync a playlist."""
        uuid = call.data.get("uuid")
        if not uuid:
            _LOGGER.error("UUID is required for sync_playlist service")
            return
        
        try:
            await api_client.async_sync_playlist(uuid)
            await coordinator.async_request_refresh()
            _LOGGER.info("Playlist %s synced successfully", uuid)
        except Exception as err:
            _LOGGER.error("Failed to sync playlist %s: %s", uuid, err)
    
    async def sync_epg_service(call: ServiceCall) -> None:
        """Service to sync an EPG."""
        uuid = call.data.get("uuid")
        if not uuid:
            _LOGGER.error("UUID is required for sync_epg service")
            return
        
        try:
            await api_client.async_sync_epg(uuid)
            await coordinator.async_request_refresh()
            _LOGGER.info("EPG %s synced successfully", uuid)
        except Exception as err:
            _LOGGER.error("Failed to sync EPG %s: %s", uuid, err)
    
    async def refresh_data_service(call: ServiceCall) -> None:
        """Service to refresh all data."""
        try:
            await coordinator.async_request_refresh()
            _LOGGER.info("M3U Editor data refreshed successfully")
        except Exception as err:
            _LOGGER.error("Failed to refresh M3U Editor data: %s", err)
    
    # Register services
    await async_register_admin_service(
        hass,
        DOMAIN,
        SERVICE_SYNC_PLAYLIST,
        sync_playlist_service,
        schema={
            "uuid": str,
        },
    )
    
    await async_register_admin_service(
        hass,
        DOMAIN,
        SERVICE_SYNC_EPG,
        sync_epg_service,
        schema={
            "uuid": str,
        },
    )
    
    await async_register_admin_service(
        hass,
        DOMAIN,
        SERVICE_REFRESH_DATA,
        refresh_data_service,
    )
