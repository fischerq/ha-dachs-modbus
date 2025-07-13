"""Config flow for Senertec Dachs Modbus integration."""

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_GLT_PIN

_LOGGER = logging.getLogger(__name__)


class DachsModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Senertec Dachs Modbus."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()
            try:
                # Here you would typically validate the user input, e.g.,
                # try to connect to the device. For this example, we'll
                # just assume the input is valid.
                return self.async_create_entry(title="Senertec Dachs", data=user_input)
            except HomeAssistantError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=502): int,
                    vol.Required(CONF_GLT_PIN): str,
                    vol.Required(CONF_SCAN_INTERVAL, default=30): int,
                }
            ),
            errors=errors,
        )
