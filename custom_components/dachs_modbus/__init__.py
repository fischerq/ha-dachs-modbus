"""The modbus_template integration."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import ModbusTemplateDataUpdateCoordinator
from .modbus_api import ModbusApiClient
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL_SECS

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=DEFAULT_SCAN_INTERVAL_MINS)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Braiins Pool from a config entry."""
 hass.data.setdefault(DOMAIN, {})

 api_client = ModbusApiClient(hass, entry.data)

 coordinator = ModbusTemplateDataUpdateCoordinator(
        hass,
        api_client=api_client,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
