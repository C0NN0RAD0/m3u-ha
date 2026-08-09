"""Media Player platform for M3U Editor integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    ATTR_UUID,
    ATTR_NAME,
    DOMAIN,
    ENTITY_TYPE_CHANNEL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the M3U Editor media players."""
    _LOGGER.debug("Setting up M3U Editor media players")
    
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api_client = hass.data[DOMAIN][entry.entry_id]["api"]
    
    # Create media players for playlists
    playlists = coordinator.data.get("playlists", [])
    media_players = []
    
    for playlist in playlists:
        media_players.append(
            M3UEditorPlaylistMediaPlayer(
                coordinator=coordinator,
                api_client=api_client,
                playlist=playlist,
            )
        )
    
    async_add_entities(media_players)


class M3UEditorPlaylistMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    """Media player for M3U Editor playlist."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        api_client: Any,
        playlist: dict[str, Any],
    ) -> None:
        """Initialize the playlist media player."""
        super().__init__(coordinator)
        self._api_client = api_client
        
        unique_id = playlist.get(ATTR_UUID, "unknown")
        name = playlist.get(ATTR_NAME, f"Playlist {unique_id}")
        
        self._attr_unique_id = f"{DOMAIN}_{ENTITY_TYPE_CHANNEL}_{unique_id}_media_player"
        self._attr_name = name
        self._playlist = playlist
        
        # Media player attributes
        self._attr_state = MediaPlayerState.IDLE
        self._attr_media_content_type = MediaType.CHANNEL
        self._attr_supported_features = (
            MediaPlayerEntityFeature.PLAY_MEDIA
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_UUID: self._playlist.get(ATTR_UUID),
            ATTR_NAME: self._playlist.get(ATTR_NAME),
        }

    async def async_play_media(
        self,
        media_type: MediaType | str,
        media_id: str,
        enqueue: str | None = None,
        announce: bool | None = None,
        **kwargs: Any,
    ) -> None:
        """Play media from a URL or identifier."""
        # This would integrate with the m3u-proxy to play a channel
        # For now, we'll just log the action
        _LOGGER.info("Playing media: %s (type: %s)", media_id, media_type)
        self._attr_state = MediaPlayerState.PLAYING
        self.async_write_ha_state()

    async def async_media_play(self) -> None:
        """Play the media player."""
        self._attr_state = MediaPlayerState.PLAYING
        self.async_write_ha_state()

    async def async_media_pause(self) -> None:
        """Pause the media player."""
        self._attr_state = MediaPlayerState.PAUSED
        self.async_write_ha_state()

    async def async_media_stop(self) -> None:
        """Stop the media player."""
        self._attr_state = MediaPlayerState.IDLE
        self.async_write_ha_state()
