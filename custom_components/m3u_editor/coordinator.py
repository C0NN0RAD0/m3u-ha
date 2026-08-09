"""Data update coordinator for M3U Editor integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import M3UEditorAPI
from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class M3UEditorDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the M3U Editor API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: M3UEditorAPI,
        update_interval: timedelta = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self._api_client = api_client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the M3U Editor API."""
        try:
            data: dict[str, Any] = {}
            
            # Get playlists
            try:
                playlists = await self._api_client.async_get_playlists()
                data["playlists"] = playlists
            except Exception as err:
                _LOGGER.warning("Failed to get playlists: %s", err)
                data["playlists"] = []
            
            # Get EPGs
            try:
                epgs = await self._api_client.async_get_epgs()
                data["epgs"] = epgs
            except Exception as err:
                _LOGGER.warning("Failed to get EPGs: %s", err)
                data["epgs"] = []
            
            # Get channels
            try:
                channels = await self._api_client.async_get_channels()
                data["channels"] = channels
            except Exception as err:
                _LOGGER.warning("Failed to get channels: %s", err)
                data["channels"] = []
            
            return data
        
        except Exception as err:
            raise UpdateFailed(f"Failed to update M3U Editor data: {err}") from err
