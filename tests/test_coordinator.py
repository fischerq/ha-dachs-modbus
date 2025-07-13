"""Unit tests for the Dachs Modbus coordinator."""

import pytest
from datetime import timedelta
from unittest.mock import AsyncMock

from homeassistant.helpers.update_coordinator import UpdateFailed
from custom_components.dachs_modbus.coordinator import DachsModbusDataUpdateCoordinator
from custom_components.dachs_modbus.api import DachsModbusApiClient

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_successful_update(hass):
    "Test successful data update."
    mock_api_client = AsyncMock(spec=DachsModbusApiClient)
    mock_api_client.get_data.return_value = {"test": "data"}

    coordinator = DachsModbusDataUpdateCoordinator(
        hass, mock_api_client
    )
    await coordinator.async_refresh()

    assert coordinator.last_update_success is True
    assert coordinator.data == {"test": "data"}
    mock_api_client.get_data.assert_called_once()


@pytest.mark.asyncio
async def test_update_failed_api_error(hass):
    "Test data update failure due to API error."
    mock_api_client = AsyncMock(spec=DachsModbusApiClient)
    mock_api_client.get_data.side_effect = Exception("API Error")

    coordinator = DachsModbusDataUpdateCoordinator(
        hass, mock_api_client
    )
    with pytest.raises(UpdateFailed):
        await coordinator.async_refresh()

    assert coordinator.last_update_success is False
    mock_api_client.get_data.assert_called_once()
