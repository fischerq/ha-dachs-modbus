"""Number entities for the Senertec Dachs Modbus integration."""

import logging

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfPower

from .const import DOMAIN, SENSOR_PREFIX, SET_ELECTRICAL_POWER
from .coordinator import DachsModbusDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

NUMBER_TYPES: tuple[NumberEntityDescription, ...] = (
    NumberEntityDescription(
        key=SET_ELECTRICAL_POWER,
        name="Set Electrical Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        native_step=10,
    ),
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the number platform."""
    coordinator: DachsModbusDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        DachsModbusNumber(coordinator, description, config_entry)
        for description in NUMBER_TYPES
    ]
    async_add_entities(entities)


class DachsModbusNumber(CoordinatorEntity, NumberEntity):
    """Representation of a Senertec Dachs Modbus number."""

    def __init__(
        self, coordinator, entity_description, config_entry
    ):
        """Initialize the number."""
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
    def native_value(self) -> float | None:
        """Return the state of the entity."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        return self.coordinator.data.get("nominal_power")

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self.hass.async_to_executor(
            self.coordinator.api.set_electrical_power, int(value)
        )
        await self.coordinator.async_request_refresh()
