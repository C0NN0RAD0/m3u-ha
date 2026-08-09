"""Sensor platform for M3U Editor integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENTITY_CATEGORY_DIAGNOSTIC
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    ATTR_CHANNEL_COUNT,
    ATTR_EPG_COUNT,
    ATTR_LAST_SYNC,
    ATTR_PLAYLIST_ID,
    ATTR_PLAYLIST_NAME,
    ATTR_STATUS,
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
    """Set up the M3U Editor sensors."""
    _LOGGER.debug("Setting up M3U Editor sensors")
    
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    # Create sensors for playlists
    playlists = coordinator.data.get("playlists", [])
    sensors = []
    
    for playlist in playlists:
        sensors.append(
            M3UEditorPlaylistSensor(
                coordinator=coordinator,
                playlist=playlist,
            )
        )
    
    # Create sensors for EPGs
    epgs = coordinator.data.get("epgs", [])
    for epg in epgs:
        sensors.append(
            M3UEditorEpgSensor(
                coordinator=coordinator,
                epg=epg,
            )
        )
    
    async_add_entities(sensors)


class M3UEditorBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for M3U Editor sensors."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entity_type: str,
        unique_id: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{entity_type}_{unique_id}"
        self._attr_name = name
        self._attr_entity_category = ENTITY_CATEGORY_DIAGNOSTIC


class M3UEditorPlaylistSensor(M3UEditorBaseSensor):
    """Sensor for M3U Editor playlist."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        playlist: dict[str, Any],
    ) -> None:
        """Initialize the playlist sensor."""
        unique_id = playlist.get(ATTR_UUID, playlist.get(ATTR_PLAYLIST_ID, "unknown"))
        name = playlist.get(ATTR_PLAYLIST_NAME, f"Playlist {unique_id}")
        
        super().__init__(
            coordinator=coordinator,
            entity_type=ENTITY_TYPE_PLAYLIST,
            unique_id=str(unique_id),
            name=name,
        )
        
        self._playlist = playlist
        self._attr_native_value = playlist.get(ATTR_CHANNEL_COUNT, 0)
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "channels"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_PLAYLIST_ID: self._playlist.get(ATTR_PLAYLIST_ID),
            ATTR_PLAYLIST_NAME: self._playlist.get(ATTR_PLAYLIST_NAME),
            ATTR_UUID: self._playlist.get(ATTR_UUID),
            ATTR_CHANNEL_COUNT: self._playlist.get(ATTR_CHANNEL_COUNT),
            ATTR_LAST_SYNC: self._playlist.get(ATTR_LAST_SYNC),
            ATTR_STATUS: self._playlist.get(ATTR_STATUS),
        }


class M3UEditorEpgSensor(M3UEditorBaseSensor):
    """Sensor for M3U Editor EPG."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        epg: dict[str, Any],
    ) -> None:
        """Initialize the EPG sensor."""
        unique_id = epg.get(ATTR_UUID, epg.get("id", "unknown"))
        name = epg.get("name", f"EPG {unique_id}")
        
        super().__init__(
            coordinator=coordinator,
            entity_type=ENTITY_TYPE_EPG,
            unique_id=str(unique_id),
            name=name,
        )
        
        self._epg = epg
        self._attr_native_value = epg.get(ATTR_EPG_COUNT, 0)
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "programmes"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_UUID: self._epg.get(ATTR_UUID),
            "name": self._epg.get("name"),
            ATTR_EPG_COUNT: self._epg.get(ATTR_EPG_COUNT),
            ATTR_LAST_SYNC: self._epg.get(ATTR_LAST_SYNC),
            ATTR_STATUS: self._epg.get(ATTR_STATUS),
        }



