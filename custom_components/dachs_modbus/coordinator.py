"""Data update coordinator for the Senertec Dachs Modbus integration."""

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DachsModbusApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class DachsModbusDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: DachsModbusApiClient) -> None:
        """Initialize."""
        self.api = client
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.hass.async_to_executor(self.api.get_data)
        except Exception as exception:
            raise UpdateFailed(exception) from exception
