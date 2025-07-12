"""Sensor entities for the new integration."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_DEVICE_NAME
from .coordinator import DeviceDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Define your sensor types here as a tuple of SensorEntityDescription objects
SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    # Example Sensor: Replace with your device's sensor definitions
    # SensorEntityDescription(
    #     key="example_value",
    #     name="Example Sensor Value",
    #     icon="mdi:gauge",
    #     native_unit_of_measurement="Units",
    #     state_class=SensorStateClass.MEASUREMENT,
    # ),
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    coordinator: DeviceDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    device_name = config_entry.data.get(CONF_DEVICE_NAME)

    entities = [
        DeviceSensor(coordinator, description, config_entry)
        for description in SENSOR_TYPES
    ]
    async_add_entities(entities)


class DeviceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a device sensor."""

    def __init__(
        self, coordinator, entity_description, config_entry
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._config_entry = config_entry
        self._attr_name = f"{config_entry.data.get(CONF_DEVICE_NAME)} {entity_description.name}"
        self._attr_unique_id = (
            f"{self._config_entry.entry_id}_{self.entity_description.key}"
        )

    @property
    def device_info(self):
        """Return device information."""
        device_name = self._config_entry.data.get(
            CONF_DEVICE_NAME, "Device"
        )
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": device_name,
            "manufacturer": "Your Manufacturer", # Replace with your manufacturer
            "model": "Your Model", # Replace with your model
            "entry_type": "service",
        }

    @property
    def native_value(self):
        """Return the state of the sensor, handling potential missing data."""
        # Access data from the coordinator's data attribute
        return self.coordinator.data.get(self.entity_description.key, None)
