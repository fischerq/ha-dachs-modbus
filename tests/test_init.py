import pytest
from unittest.mock import patch, MagicMock

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL

from custom_components.dachs_modbus.const import DOMAIN, CONF_GLT_PIN
from custom_components.dachs_modbus.coordinator import DachsModbusDataUpdateCoordinator
from custom_components.dachs_modbus import async_setup_entry, async_unload_entry

MOCK_HOST = "1.2.3.4"
MOCK_PORT = 502
MOCK_GLT_PIN = "1234"
MOCK_SCAN_INTERVAL = 60
MOCK_ENTRY_ID = "mock_entry_1"


@pytest.fixture
def mock_config_entry():
    """Mock a config entry."""
    return MagicMock(
        data={
            CONF_HOST: MOCK_HOST,
            CONF_PORT: MOCK_PORT,
            CONF_GLT_PIN: MOCK_GLT_PIN,
            CONF_SCAN_INTERVAL: MOCK_SCAN_INTERVAL,
        },
        entry_id=MOCK_ENTRY_ID,
        title="Senertec Dachs",
    )


@patch("custom_components.dachs_modbus.DachsModbusApiClient")
@patch(
    "custom_components.dachs_modbus.DachsModbusDataUpdateCoordinator.async_config_entry_first_refresh",
    return_value=None,
)  # Mock first refresh
@patch(
    "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups"
)  # Further mock sensor setup
async def test_async_setup_entry(
    mock_forward_setup,
    mock_first_refresh,
    MockDachsModbusApiClient,
    hass: HomeAssistant,
    mock_config_entry,
):
    """Test successful setup of the integration."""
    # Mock the API client instance
    mock_api_client_instance = MockDachsModbusApiClient.return_value

    success = await async_setup_entry(hass, mock_config_entry)
    await hass.async_block_till_done()

    assert success is True
    MockDachsModbusApiClient.assert_called_once_with(
        host=MOCK_HOST,
        port=MOCK_PORT,
        glt_pin=MOCK_GLT_PIN,
        scan_interval=MOCK_SCAN_INTERVAL,
    )

    # Check that coordinator is created and stored
    assert MOCK_ENTRY_ID in hass.data[DOMAIN]
    coordinator = hass.data[DOMAIN][MOCK_ENTRY_ID]
    assert isinstance(coordinator, DachsModbusDataUpdateCoordinator)
    assert coordinator.api == mock_api_client_instance

    mock_first_refresh.assert_called_once()
    mock_forward_setup.assert_called_once_with(
        mock_config_entry, ["sensor", "number", "switch"]
    )


@patch("homeassistant.config_entries.ConfigEntries.async_unload_platforms")
async def test_async_unload_entry(
    mock_unload_platforms,
    hass: HomeAssistant,
    mock_config_entry,
):
    """Test successful unload of the integration."""
    # Pre-populate hass.data as if setup was successful
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][mock_config_entry.entry_id] = MagicMock()  # Mock coordinator
    mock_unload_platforms.return_value = True

    success = await async_unload_entry(hass, mock_config_entry)
    await hass.async_block_till_done()

    assert success is True
    mock_unload_platforms.assert_called_once_with(
        mock_config_entry, ["sensor", "number", "switch"]
    )
    assert mock_config_entry.entry_id not in hass.data[DOMAIN]
