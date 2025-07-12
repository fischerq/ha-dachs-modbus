"""Config flow for Braiins Pool integration."""

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class YourIntegrationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
 """Handle a config flow for your integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
 return self._show_config_form(user_input)

        errors = {}

        if not user_input.get(CONF_API_KEY):
            errors["base"] = "invalid_api_key"  # Use a specific error code

        rewards_account_name = user_input.get(CONF_REWARDS_ACCOUNT_NAME)

        if not errors:
            # Check if already configured (if only one instance is allowed)
 # Replace with a unique ID based on your device/service
            await self.async_set_unique_id("YOUR_UNIQUE_ID")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=rewards_account_name, data=user_input)

        return self._show_config_form(user_input, errors)

    def _show_config_form(self, user_input=None, errors=None):
        """Show the configuration form to the user."""
        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            last_step=True,
        )
