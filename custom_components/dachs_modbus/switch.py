"""Switch entities for the Senertec Dachs Modbus integration."""

import logging

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_PREFIX, BLOCK_CHP_VIA_GLT
from .coordinator import DachsModbusDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SWITCH_TYPES: tuple[SwitchEntityDescription, ...] = (
    SwitchEntityDescription(
        key=BLOCK_CHP_VIA_GLT,
        name="Block CHP via GLT",
    ),
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the switch platform."""
    coordinator: DachsModbusDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        DachsModbusSwitch(coordinator, description, config_entry)
        for description in SWITCH_TYPES
    ]
    async_add_entities(entities)


class DachsModbusSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Senertec Dachs Modbus switch."""

    def __init__(
        self, coordinator, entity_description, config_entry
    ):
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._config_entry = config_entry
        self._attr_name = f"{SENSOR_PREFIX} {entity_description.name}"
        self._attr_unique_id = (
            f"{self._config_entry.entry_id}_{self.entity_description.key}"
        )

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": SENSOR_PREFIX,
            "manufacturer": "Senertec",
            "model": "Dachs",
            "entry_type": "service",
        }

    @property
    def is_on(self) -> bool | None:
        """Return the state of the entity."""
        return self.coordinator.data.get(self.entity_description.key)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        await self.hass.async_to_executor(
            self.coordinator.api.set_block_chp, True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        await self.hass.async_to_executor(
            self.coordinator.api.set_block_chp, False
        )
        await self.coordinator.async_request_refresh()
