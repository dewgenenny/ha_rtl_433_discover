"""Config flow for rtl_433 Discovery integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_TOPIC_PREFIX, DEFAULT_TOPIC_PREFIX, CONF_IGNORE_DEVICES

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TOPIC_PREFIX, default=DEFAULT_TOPIC_PREFIX): str,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for rtl_433 Discovery."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        # Basic validation (could be expanded to check MQTT connectivity if needed, 
        # but pure string validation is usually enough for a topic)
        

        return self.async_create_entry(title="rtl_433 Bridge", data=user_input)

    async def async_step_discovery(
        self, discovery_info: dict[str, Any]
    ) -> FlowResult:
        """Handle discovery."""
        unique_id = discovery_info["unique_id"]
        model = discovery_info["model"]
        
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured(updates=discovery_info)

        self.context["title_placeholders"] = {"name": f"{model} {unique_id}"}
        
        if "confirm" not in discovery_info:
             # Store info for the form step
             self.discovery_data = discovery_info
             return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        if user_input is not None:
             return self.async_create_entry(
                 title=f"{self.discovery_data['model']} {self.discovery_data['unique_id']}",
                 data=self.discovery_data
             )
             
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={"name": f"{self.discovery_data['model']} {self.discovery_data['unique_id']}"}
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_IGNORE_DEVICES,
                        default=self.config_entry.options.get(CONF_IGNORE_DEVICES, ""),
                    ): str,
                }
            ),
        )
