"""Sensor entities for the Senertec Dachs Modbus integration."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DachsModbusDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Define your sensor types here as a tuple of SensorEntityDescription objects
SENSOR_TYPES: tuple[SensorEntityDescription, ...] = ()


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    coordinator: DachsModbusDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        DachsModbusSensor(coordinator, description, config_entry)
        for description in SENSOR_TYPES
    ]
    async_add_entities(entities)


class DachsModbusSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Senertec Dachs Modbus sensor."""

    def __init__(
        self, coordinator, entity_description, config_entry
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._config_entry = config_entry
        self._attr_name = f"Senertec Dachs {entity_description.name}"
        self._attr_unique_id = (
            f"{self._config_entry.entry_id}_{self.entity_description.key}"
        )

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Senertec Dachs",
            "manufacturer": "Senertec",
            "model": "Dachs",
            "entry_type": "service",
        }

    @property
    def native_value(self):
        """Return the state of the sensor, handling potential missing data."""
        return self.coordinator.data.get(self.entity_description.key, None)
