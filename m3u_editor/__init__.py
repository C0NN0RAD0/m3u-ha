"""M3U Editor integration for Home Assistant."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import M3UEditorAPI
from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import M3UEditorDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.MEDIA_PLAYER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up M3U Editor from a config entry."""
    _LOGGER.debug("Setting up M3U Editor integration")
    
    # Store the config entry data
    hass.data.setdefault(DOMAIN, {})
    
    # Create API client
    api_client = M3UEditorAPI(entry.data)
    
    # Get scan interval from options or use default
    scan_interval = timedelta(
        seconds=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL.seconds)
    )
    
    # Create coordinator
    coordinator = M3UEditorDataUpdateCoordinator(
        hass=hass,
        api_client=api_client,
        update_interval=scan_interval,
    )
    
    # Store data
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api_client,
        "coordinator": coordinator,
        "config": entry.data,
    }
    
    # Initial data fetch
    await coordinator.async_config_entry_first_refresh()
    
    # Forward the setup to each platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading M3U Editor integration")
    
    # Close API client
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        api_client = hass.data[DOMAIN][entry.entry_id].get("api")
        if api_client:
            await api_client.close()
    
    # Unload all platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    # Clean up data
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry."""
    _LOGGER.debug("Reloading M3U Editor integration")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate an old config entry to a new version."""
    _LOGGER.debug("Migrating M3U Editor config entry")
    return True
