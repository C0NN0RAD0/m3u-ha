"""Config flow for M3U Editor integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from aiohttp import ClientError

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_SCAN_INTERVAL,
    CONF_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_PROTOCOL,
    DOMAIN,
    ERROR_CANNOT_CONNECT,
    ERROR_INVALID_AUTH,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_PROTOCOL, default=DEFAULT_PROTOCOL): vol.In(["http", "https"]),
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
        vol.Optional(CONF_API_KEY): str,
        vol.Optional(CONF_SSL, default=False): bool,
        vol.Optional(CONF_VERIFY_SSL, default=True): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    host = data[CONF_HOST]
    port = data[CONF_PORT]
    protocol = data[CONF_PROTOCOL]
    username = data.get(CONF_USERNAME)
    password = data.get(CONF_PASSWORD)
    api_key = data.get(CONF_API_KEY)
    ssl = data.get(CONF_SSL, False)
    verify_ssl = data.get(CONF_VERIFY_SSL, True)
    
    # Build the base URL
    base_url = f"{protocol}://{host}:{port}"
    
    session = async_get_clientsession(hass)
    
    try:
        # Try to connect to the API
        # First, try with API key if provided
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Try the system info endpoint (public)
        url = f"{base_url}/api/system/info"
        
        async with session.get(
            url,
            headers=headers,
            ssl=verify_ssl if ssl else False,
            timeout=10,
        ) as response:
            if response.status == 200:
                return {"base_url": base_url, **data}
            elif response.status == 401:
                # Try with username/password
                if username and password:
                    # Try to authenticate using Dispatcharr-compatible endpoint
                    auth_url = f"{base_url}/api/accounts/token"
                    auth_data = {
                        "username": username,
                        "password": password,
                    }
                    
                    async with session.post(
                        auth_url,
                        json=auth_data,
                        ssl=verify_ssl if ssl else False,
                        timeout=10,
                    ) as auth_response:
                        if auth_response.status == 200:
                            auth_data = await auth_response.json()
                            if "access" in auth_data:
                                # Store the token for later use
                                data["access_token"] = auth_data["access"]
                                data["refresh_token"] = auth_data.get("refresh")
                                return {"base_url": base_url, **data}
                        raise InvalidAuth
                raise InvalidAuth
            else:
                raise CannotConnect
    
    except ClientError as err:
        _LOGGER.error("Error connecting to M3U Editor API: %s", err)
        raise CannotConnect from err
    except Exception as err:
        _LOGGER.error("Unexpected error: %s", err)
        raise CannotConnect from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for M3U Editor."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}
        
        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            # Check if we already have a config entry with this host
            await self.async_set_unique_id(info["base_url"])
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=user_input.get(CONF_HOST, DEFAULT_HOST),
                data=user_input,
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, import_config: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_config)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for M3U Editor."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options flow."""
        if user_input is not None:
            self.options.update(user_input)
            return self.async_create_entry(title="", data=self.options)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.options.get(CONF_SCAN_INTERVAL, 300),
                    ): int,
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
