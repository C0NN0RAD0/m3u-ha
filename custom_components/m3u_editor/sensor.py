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
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    ATTR_UUID,
    ATTR_NAME,
    ATTR_TOTAL_CHANNELS,
    ATTR_ENABLED_CHANNELS,
    ATTR_LIVE_CHANNELS,
    ATTR_VOD_CHANNELS,
    ATTR_GROUPS_COUNT,
    ATTR_PROXY_ENABLED,
    ATTR_ACTIVE_STREAMS,
    ATTR_CHANNEL_COUNT,
    ATTR_LAST_SYNC,
    ATTR_STATUS,
    ATTR_SOURCE_TYPE,
    ATTR_IS_PROCESSING,
    ATTR_PROXY_HEALTH,
    ATTR_TOTAL_CLIENTS,
    ATTR_BANDWIDTH_KBPS,
    ATTR_MODE,
    ATTR_PROXY_URL,
    ATTR_STREAMS_BY_PLAYLIST,
    DOMAIN,
    ENTITY_TYPE_EPG,
    ENTITY_TYPE_PLAYLIST,
    ENTITY_TYPE_PROXY,
    ENTITY_TYPE_SYSTEM,
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
    sensors: list[M3UEditorBaseSensor] = []
    
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
    
    # Create system sensor
    if "system_stats" in coordinator.data and coordinator.data["system_stats"]:
        sensors.append(M3UEditorSystemSensor(coordinator, coordinator.data["system_stats"]))
        
    # Create proxy sensors
    if "proxy_status" in coordinator.data and coordinator.data["proxy_status"]:
        sensors.append(M3UEditorProxySensor(coordinator, coordinator.data["proxy_status"]))
        
    if "proxy_streams" in coordinator.data and coordinator.data["proxy_streams"]:
        sensors.append(M3UEditorProxyStreamsSensor(coordinator, coordinator.data["proxy_streams"]))
    
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
        self._attr_entity_category = EntityCategory.DIAGNOSTIC


class M3UEditorPlaylistSensor(M3UEditorBaseSensor):
    """Sensor for M3U Editor playlist."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        playlist: dict[str, Any],
    ) -> None:
        """Initialize the playlist sensor."""
        unique_id = playlist.get(ATTR_UUID, "unknown")
        name = playlist.get(ATTR_NAME, f"Playlist {unique_id}")
        
        super().__init__(
            coordinator=coordinator,
            entity_type=ENTITY_TYPE_PLAYLIST,
            unique_id=str(unique_id),
            name=name,
        )
        
        self._playlist = playlist
        self._attr_native_value = playlist.get(ATTR_TOTAL_CHANNELS, 0)
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "channels"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_UUID: self._playlist.get(ATTR_UUID),
            ATTR_NAME: self._playlist.get(ATTR_NAME),
            ATTR_TOTAL_CHANNELS: self._playlist.get(ATTR_TOTAL_CHANNELS),
            ATTR_ENABLED_CHANNELS: self._playlist.get(ATTR_ENABLED_CHANNELS),
            ATTR_LIVE_CHANNELS: self._playlist.get(ATTR_LIVE_CHANNELS),
            ATTR_VOD_CHANNELS: self._playlist.get(ATTR_VOD_CHANNELS),
            ATTR_GROUPS_COUNT: self._playlist.get(ATTR_GROUPS_COUNT),
            ATTR_PROXY_ENABLED: self._playlist.get(ATTR_PROXY_ENABLED),
            ATTR_ACTIVE_STREAMS: self._playlist.get(ATTR_ACTIVE_STREAMS),
            ATTR_LAST_SYNC: self._playlist.get(ATTR_LAST_SYNC),
            ATTR_STATUS: self._playlist.get(ATTR_STATUS),
            ATTR_SOURCE_TYPE: self._playlist.get(ATTR_SOURCE_TYPE),
        }


class M3UEditorEpgSensor(M3UEditorBaseSensor):
    """Sensor for M3U Editor EPG."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        epg: dict[str, Any],
    ) -> None:
        """Initialize the EPG sensor."""
        unique_id = epg.get(ATTR_UUID, "unknown")
        name = epg.get(ATTR_NAME, f"EPG {unique_id}")
        
        super().__init__(
            coordinator=coordinator,
            entity_type=ENTITY_TYPE_EPG,
            unique_id=str(unique_id),
            name=name,
        )
        
        self._epg = epg
        self._attr_native_value = epg.get(ATTR_CHANNEL_COUNT, 0)
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "channels"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_UUID: self._epg.get(ATTR_UUID),
            ATTR_NAME: self._epg.get(ATTR_NAME),
            ATTR_CHANNEL_COUNT: self._epg.get(ATTR_CHANNEL_COUNT),
            ATTR_LAST_SYNC: self._epg.get(ATTR_LAST_SYNC),
            ATTR_STATUS: self._epg.get(ATTR_STATUS),
            ATTR_SOURCE_TYPE: self._epg.get(ATTR_SOURCE_TYPE),
            ATTR_IS_PROCESSING: self._epg.get(ATTR_IS_PROCESSING),
        }


class M3UEditorSystemSensor(M3UEditorBaseSensor):
    """Representation of a system status sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        system_stats: dict[str, Any],
    ) -> None:
        """Initialize the system sensor."""
        super().__init__(
            coordinator=coordinator,
            entity_type=ENTITY_TYPE_SYSTEM,
            unique_id="system_total_channels",
            name="Total Channels",
        )
        self._system_stats = system_stats
        self._attr_native_value = system_stats.get("total_channels", 0)
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "channels"


class M3UEditorProxySensor(M3UEditorBaseSensor):
    """Representation of a proxy status sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        proxy_status: dict[str, Any],
    ) -> None:
        """Initialize the proxy sensor."""
        super().__init__(
            coordinator=coordinator,
            entity_type=ENTITY_TYPE_PROXY,
            unique_id="proxy_status",
            name="Proxy Status",
        )
        self._proxy_status = proxy_status
        self._attr_native_value = proxy_status.get(ATTR_PROXY_HEALTH, "unknown").title()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_MODE: self._proxy_status.get(ATTR_MODE),
            ATTR_PROXY_URL: self._proxy_status.get(ATTR_PROXY_URL),
            ATTR_STREAMS_BY_PLAYLIST: self._proxy_status.get(ATTR_STREAMS_BY_PLAYLIST, []),
        }


class M3UEditorProxyStreamsSensor(M3UEditorBaseSensor):
    """Representation of a proxy active streams sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        proxy_streams: dict[str, Any],
    ) -> None:
        """Initialize the proxy streams sensor."""
        super().__init__(
            coordinator=coordinator,
            entity_type=ENTITY_TYPE_PROXY,
            unique_id="proxy_active_streams",
            name="Active Proxy Streams",
        )
        self._proxy_streams = proxy_streams
        stats = proxy_streams.get("globalStats", {})
        self._attr_native_value = stats.get("active_streams", 0)
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "streams"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        stats = self._proxy_streams.get("globalStats", {})
        return {
            ATTR_TOTAL_CLIENTS: stats.get("total_clients", 0),
            ATTR_BANDWIDTH_KBPS: stats.get("total_bandwidth_kbps", 0),
        }



