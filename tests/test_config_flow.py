import pytest
from unittest.mock import patch
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.data_entry_flow import FlowResultType

from custom_components.dachs_modbus.const import DOMAIN, CONF_GLT_PIN

MOCK_HOST = "1.2.3.4"
MOCK_PORT = 502
MOCK_GLT_PIN = "1234"
MOCK_SCAN_INTERVAL = 60


@pytest.fixture(autouse=True)
def mock_setup_entry():
    """Mock async_setup_entry to bypass actual setup."""
    with patch(
        "custom_components.dachs_modbus.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup


async def test_config_flow_user_step(hass: HomeAssistant):
    """Test the user config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not result["errors"]

    # Test successful submission
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: MOCK_HOST,
            CONF_PORT: MOCK_PORT,
            CONF_GLT_PIN: MOCK_GLT_PIN,
            CONF_SCAN_INTERVAL: MOCK_SCAN_INTERVAL,
        },
    )
    await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Senertec Dachs"
    assert result2["data"] == {
        CONF_HOST: MOCK_HOST,
        CONF_PORT: MOCK_PORT,
        CONF_GLT_PIN: MOCK_GLT_PIN,
        CONF_SCAN_INTERVAL: MOCK_SCAN_INTERVAL,
    }


async def test_config_flow_already_configured(hass: HomeAssistant):
    """Test config flow when an entry with the same unique ID (host) already exists."""
    # Create a mock entry first
    mock_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=MOCK_HOST,
        data={
            CONF_HOST: MOCK_HOST,
            CONF_PORT: MOCK_PORT,
            CONF_GLT_PIN: MOCK_GLT_PIN,
            CONF_SCAN_INTERVAL: MOCK_SCAN_INTERVAL,
        },
        title="Senertec Dachs",
    )
    mock_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    # Try to configure a new flow with the same host
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: MOCK_HOST,
            CONF_PORT: MOCK_PORT,
            CONF_GLT_PIN: MOCK_GLT_PIN,
            CONF_SCAN_INTERVAL: MOCK_SCAN_INTERVAL,
        },
    )
    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"
