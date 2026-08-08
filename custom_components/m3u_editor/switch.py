"""Switch platform for M3U Editor integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    ATTR_PLAYLIST_ID,
    ATTR_PLAYLIST_NAME,
    ATTR_UUID,
    DOMAIN,
    ENTITY_TYPE_PLAYLIST,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the M3U Editor switches."""
    _LOGGER.debug("Setting up M3U Editor switches")
    
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    # Create switches for playlist auto-sync
    playlists = coordinator.data.get("playlists", [])
    switches = []
    
    for playlist in playlists:
        switches.append(
            M3UEditorPlaylistAutoSyncSwitch(
                coordinator=coordinator,
                playlist=playlist,
            )
        )
    
    async_add_entities(switches)


class M3UEditorBaseSwitch(CoordinatorEntity, SwitchEntity):
    """Base class for M3U Editor switches."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entity_type: str,
        unique_id: str,
        name: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{entity_type}_{unique_id}_switch"
        self._attr_name = name
        self._attr_device_class = SwitchDeviceClass.SWITCH


class M3UEditorPlaylistAutoSyncSwitch(M3UEditorBaseSwitch):
    """Switch for M3U Editor playlist auto-sync."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        playlist: dict[str, Any],
    ) -> None:
        """Initialize the playlist auto-sync switch."""
        unique_id = playlist.get(ATTR_UUID, playlist.get(ATTR_PLAYLIST_ID, "unknown"))
        name = f"{playlist.get(ATTR_PLAYLIST_NAME, f'Playlist {unique_id}')} Auto Sync"
        
        super().__init__(
            coordinator=coordinator,
            entity_type=ENTITY_TYPE_PLAYLIST,
            unique_id=str(unique_id),
            name=name,
        )
        
        self._playlist = playlist
        self._attr_is_on = playlist.get("auto_sync", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_PLAYLIST_ID: self._playlist.get(ATTR_PLAYLIST_ID),
            ATTR_PLAYLIST_NAME: self._playlist.get(ATTR_PLAYLIST_NAME),
            ATTR_UUID: self._playlist.get(ATTR_UUID),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on auto-sync for the playlist."""
        # This would call the API to enable auto-sync
        # For now, we'll just update the state
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off auto-sync for the playlist."""
        # This would call the API to disable auto-sync
        # For now, we'll just update the state
        self._attr_is_on = False
        self.async_write_ha_state()
