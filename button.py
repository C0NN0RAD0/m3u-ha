"""Button platform for M3U Editor integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    ATTR_EPG_COUNT,
    ATTR_LAST_SYNC,
    ATTR_PLAYLIST_ID,
    ATTR_PLAYLIST_NAME,
    ATTR_UUID,
    DOMAIN,
    ENTITY_TYPE_EPG,
    ENTITY_TYPE_PLAYLIST,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the M3U Editor buttons."""
    _LOGGER.debug("Setting up M3U Editor buttons")
    
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api_client = hass.data[DOMAIN][entry.entry_id]["api"]
    
    # Create buttons for playlists
    playlists = coordinator.data.get("playlists", [])
    buttons = []
    
    for playlist in playlists:
        buttons.append(
            M3UEditorPlaylistSyncButton(
                coordinator=coordinator,
                api_client=api_client,
                playlist=playlist,
            )
        )
    
    # Create buttons for EPGs
    epgs = coordinator.data.get("epgs", [])
    for epg in epgs:
        buttons.append(
            M3UEditorEpgSyncButton(
                coordinator=coordinator,
                api_client=api_client,
                epg=epg,
            )
        )
    
    async_add_entities(buttons)


class M3UEditorBaseButton(CoordinatorEntity, ButtonEntity):
    """Base class for M3U Editor buttons."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        api_client: Any,
        entity_type: str,
        unique_id: str,
        name: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._api_client = api_client
        self._attr_unique_id = f"{DOMAIN}_{entity_type}_{unique_id}_button"
        self._attr_name = name
        self._attr_device_class = ButtonDeviceClass.UPDATE


class M3UEditorPlaylistSyncButton(M3UEditorBaseButton):
    """Button to sync a playlist."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        api_client: Any,
        playlist: dict[str, Any],
    ) -> None:
        """Initialize the playlist sync button."""
        unique_id = playlist.get(ATTR_UUID, playlist.get(ATTR_PLAYLIST_ID, "unknown"))
        name = f"{playlist.get(ATTR_PLAYLIST_NAME, f'Playlist {unique_id}')} Sync"
        
        super().__init__(
            coordinator=coordinator,
            api_client=api_client,
            entity_type=ENTITY_TYPE_PLAYLIST,
            unique_id=str(unique_id),
            name=name,
        )
        
        self._playlist = playlist

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_PLAYLIST_ID: self._playlist.get(ATTR_PLAYLIST_ID),
            ATTR_PLAYLIST_NAME: self._playlist.get(ATTR_PLAYLIST_NAME),
            ATTR_UUID: self._playlist.get(ATTR_UUID),
            ATTR_LAST_SYNC: self._playlist.get(ATTR_LAST_SYNC),
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        uuid = self._playlist.get(ATTR_UUID)
        if uuid:
            try:
                await self._api_client.async_sync_playlist(uuid)
                # Refresh the coordinator data
                await self.coordinator.async_request_refresh()
            except Exception as err:
                _LOGGER.error("Failed to sync playlist %s: %s", uuid, err)


class M3UEditorEpgSyncButton(M3UEditorBaseButton):
    """Button to sync an EPG."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        api_client: Any,
        epg: dict[str, Any],
    ) -> None:
        """Initialize the EPG sync button."""
        unique_id = epg.get(ATTR_UUID, epg.get("id", "unknown"))
        name = f"{epg.get('name', f'EPG {unique_id}')} Sync"
        
        super().__init__(
            coordinator=coordinator,
            api_client=api_client,
            entity_type=ENTITY_TYPE_EPG,
            unique_id=str(unique_id),
            name=name,
        )
        
        self._epg = epg

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_UUID: self._epg.get(ATTR_UUID),
            "name": self._epg.get("name"),
            ATTR_EPG_COUNT: self._epg.get(ATTR_EPG_COUNT),
            ATTR_LAST_SYNC: self._epg.get(ATTR_LAST_SYNC),
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        uuid = self._epg.get(ATTR_UUID)
        if uuid:
            try:
                await self._api_client.async_sync_epg(uuid)
                # Refresh the coordinator data
                await self.coordinator.async_request_refresh()
            except Exception as err:
                _LOGGER.error("Failed to sync EPG %s: %s", uuid, err)
