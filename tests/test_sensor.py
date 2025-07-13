import pytest
from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
    SensorEntityDescription,
)

from custom_components.dachs_modbus.const import DOMAIN
from custom_components.dachs_modbus.sensor import DachsModbusSensor, SENSOR_TYPES
from custom_components.dachs_modbus.coordinator import DachsModbusDataUpdateCoordinator

MOCK_ENTRY_ID = "sensor_entry_1"


@pytest.fixture
def mock_coordinator(hass):
    """Mock DachsModbusDataUpdateCoordinator."""
    coordinator = MagicMock(spec=DachsModbusDataUpdateCoordinator)
    coordinator.hass = hass
    coordinator.data = {"test_sensor": 123}
    coordinator.config_entry = MagicMock(spec=ConfigEntry)
    coordinator.config_entry.entry_id = MOCK_ENTRY_ID
    return coordinator


@pytest.fixture
def mock_config_entry_obj():
    """Returns a mock ConfigEntry object"""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = MOCK_ENTRY_ID
    entry.title = "Senertec Dachs"
    return entry


async def test_sensor_creation_and_device_info(
    hass: HomeAssistant, mock_coordinator, mock_config_entry_obj
):
    """Test sensor creation and device info."""
    description = SensorEntityDescription(
        key="test_sensor",
        name="Test Sensor",
    )
    sensor = DachsModbusSensor(mock_coordinator, description, mock_config_entry_obj)
    sensor.hass = hass

    assert sensor.name == "Senertec Dachs Test Sensor"
    assert sensor.unique_id == f"{MOCK_ENTRY_ID}_test_sensor"
    assert sensor.native_value == 123

    device_info = sensor.device_info
    assert device_info is not None
    assert device_info["identifiers"] == {(DOMAIN, MOCK_ENTRY_ID)}
    assert device_info["name"] == "Senertec Dachs"
    assert device_info["manufacturer"] == "Senertec"
    assert device_info["model"] == "Dachs"
