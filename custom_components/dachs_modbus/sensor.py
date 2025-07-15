"""Sensor entities for the Senertec Dachs Modbus integration."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfTemperature, UnitOfPower, UnitOfTime, UnitOfEnergy

from .const import (
    DOMAIN,
    SENSOR_PREFIX,
    GLT_INTERFACE_VERSION,
    DEVICE_TYPE,
    UNIT_STATUS,
    ELECTRICAL_POWER,
    TYPE_OF_REQUEST,
    RUNTIME_SINCE_LAST_START,
    LAST_SHUTDOWN_REASON,
    HEATING_WATER_PUMP_STATUS,
    CHP_OUTLET_TEMPERATURE,
    CHP_INLET_TEMPERATURE,
    TOTAL_OPERATING_HOURS,
    TOTAL_STARTS,
    GENERATED_ELECTRICAL_ENERGY,
    GENERATED_THERMAL_ENERGY,
    OUTSIDE_TEMPERATURE,
    BUFFER_TEMPERATURE_T1,
    BUFFER_TEMPERATURE_T2,
    BUFFER_TEMPERATURE_T3,
    BUFFER_TEMPERATURE_T4,
    CONTROL_STRATEGY,
    MINIMUM_RUNTIME,
    MAX_INLET_TEMPERATURE,
    POWER_MODULATION,
    ACTIVE_GLT_CONNECTIONS,
    DEVICE_TYPES,
    UNIT_STATUS_MAP,
    TYPE_OF_REQUEST_MAP,
    LAST_SHUTDOWN_REASON_MAP,
    HEATING_WATER_PUMP_STATUS_MAP,
    CONTROL_STRATEGY_MAP,
    POWER_MODULATION_MAP,
    SERIAL_NUMBER,
    NOMINAL_POWER,
    POWER_LEVEL,
    MODULE_TYPE_DEFINITION,
    OPERATING_HOURS_POWER_LEVEL_1,
    OPERATING_HOURS_POWER_LEVEL_2,
    OPERATING_HOURS_POWER_LEVEL_3,
    CURRENT_DISCHARGE_POWER,
)
from .coordinator import DachsModbusDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Define your sensor types here as a tuple of SensorEntityDescription objects
SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=GLT_INTERFACE_VERSION,
        name="GLT Interface Version",
    ),
    SensorEntityDescription(
        key=DEVICE_TYPE,
        name="Device Type",
    ),
    SensorEntityDescription(
        key=UNIT_STATUS,
        name="Unit Status",
    ),
    SensorEntityDescription(
        key=ELECTRICAL_POWER,
        name="Electrical Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=TYPE_OF_REQUEST,
        name="Type of Request",
    ),
    SensorEntityDescription(
        key=RUNTIME_SINCE_LAST_START,
        name="Runtime Since Last Start",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=LAST_SHUTDOWN_REASON,
        name="Last Shutdown Reason",
    ),
    SensorEntityDescription(
        key=HEATING_WATER_PUMP_STATUS,
        name="Heating Water Pump Status",
    ),
    SensorEntityDescription(
        key=CHP_OUTLET_TEMPERATURE,
        name="CHP Outlet Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=CHP_INLET_TEMPERATURE,
        name="CHP Inlet Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=TOTAL_OPERATING_HOURS,
        name="Total Operating Hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=TOTAL_STARTS,
        name="Total Starts",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=GENERATED_ELECTRICAL_ENERGY,
        name="Generated Electrical Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=GENERATED_THERMAL_ENERGY,
        name="Generated Thermal Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=OUTSIDE_TEMPERATURE,
        name="Outside Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=BUFFER_TEMPERATURE_T1,
        name="Buffer Temperature T1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=BUFFER_TEMPERATURE_T2,
        name="Buffer Temperature T2",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=BUFFER_TEMPERATURE_T3,
        name="Buffer Temperature T3",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=BUFFER_TEMPERATURE_T4,
        name="Buffer Temperature T4",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=CONTROL_STRATEGY,
        name="Control Strategy",
    ),
    SensorEntityDescription(
        key=MINIMUM_RUNTIME,
        name="Minimum Runtime",
        native_unit_of_measurement=UnitOfTime.MINUTES,
    ),
    SensorEntityDescription(
        key=MAX_INLET_TEMPERATURE,
        name="Max Inlet Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=POWER_MODULATION,
        name="Power Modulation",
    ),
    SensorEntityDescription(
        key=SERIAL_NUMBER,
        name="Serial Number",
    ),
    SensorEntityDescription(
        key=NOMINAL_POWER,
        name="Nominal Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key=POWER_LEVEL,
        name="Power Level",
    ),
    SensorEntityDescription(
        key=MODULE_TYPE_DEFINITION,
        name="Module Type Definition",
    ),
    SensorEntityDescription(
        key=OPERATING_HOURS_POWER_LEVEL_1,
        name="Operating Hours Power Level 1",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=OPERATING_HOURS_POWER_LEVEL_2,
        name="Operating Hours Power Level 2",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=OPERATING_HOURS_POWER_LEVEL_3,
        name="Operating Hours Power Level 3",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=CURRENT_DISCHARGE_POWER,
        name="Current Discharge Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


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

    def __init__(self, coordinator, entity_description, config_entry):
        """Initialize the sensor."""
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
    def native_value(self):
        """Return the state of the sensor, handling potential missing data."""
        value = self.coordinator.data.get(self.entity_description.key, None)
        if value is None:
            return None

        key = self.entity_description.key
        if key == DEVICE_TYPE:
            return DEVICE_TYPES.get(value)
        if key == UNIT_STATUS:
            return UNIT_STATUS_MAP.get(value)
        if key == TYPE_OF_REQUEST:
            return TYPE_OF_REQUEST_MAP.get(value)
        if key == LAST_SHUTDOWN_REASON:
            return LAST_SHUTDOWN_REASON_MAP.get(value)
        if key == HEATING_WATER_PUMP_STATUS:
            return HEATING_WATER_PUMP_STATUS_MAP.get(value)
        if key == CONTROL_STRATEGY:
            return CONTROL_STRATEGY_MAP.get(value)
        if key == POWER_MODULATION:
            return POWER_MODULATION_MAP.get(value)

        return value
