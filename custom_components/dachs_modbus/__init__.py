"""The Senertec Dachs Modbus integration."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL

from .coordinator import DachsModbusDataUpdateCoordinator
from .api import DachsModbusApiClient
from .const import DOMAIN, CONF_GLT_PIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Senertec Dachs from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    client = DachsModbusApiClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        glt_pin=entry.data[CONF_GLT_PIN],
        scan_interval=entry.data[CONF_SCAN_INTERVAL],
    )

    coordinator = DachsModbusDataUpdateCoordinator(
        hass,
        client=client,
        update_interval=entry.data[CONF_SCAN_INTERVAL],
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor", "number", "switch"]
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["sensor", "number", "switch"]
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
