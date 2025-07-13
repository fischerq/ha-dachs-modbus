"""Constants for the Senertec Dachs Modbus integration."""

DOMAIN = "dachs_modbus"

CONF_GLT_PIN = "glt_pin"

# Sensors
SENSOR_PREFIX = "Dachs"
GLT_INTERFACE_VERSION = "glt_interface_version"
DEVICE_TYPE = "device_type"
UNIT_STATUS = "unit_status"
ELECTRICAL_POWER = "electrical_power"
TYPE_OF_REQUEST = "type_of_request"
RUNTIME_SINCE_LAST_START = "runtime_since_last_start"
LAST_SHUTDOWN_REASON = "last_shutdown_reason"
HEATING_WATER_PUMP_STATUS = "heating_water_pump_status"
CHP_OUTLET_TEMPERATURE = "chp_outlet_temperature"
CHP_INLET_TEMPERATURE = "chp_inlet_temperature"
TOTAL_OPERATING_HOURS = "total_operating_hours"
TOTAL_STARTS = "total_starts"
GENERATED_ELECTRICAL_ENERGY = "generated_electrical_energy"
GENERATED_THERMAL_ENERGY = "generated_thermal_energy"
OUTSIDE_TEMPERATURE = "outside_temperature"
BUFFER_TEMPERATURE_T1 = "buffer_temperature_t1"
BUFFER_TEMPERATURE_T2 = "buffer_temperature_t2"
BUFFER_TEMPERATURE_T3 = "buffer_temperature_t3"
BUFFER_TEMPERATURE_T4 = "buffer_temperature_t4"
CONTROL_STRATEGY = "control_strategy"
MINIMUM_RUNTIME = "minimum_runtime"
MAX_INLET_TEMPERATURE = "max_inlet_temperature"
POWER_MODULATION = "power_modulation"
ACTIVE_GLT_CONNECTIONS = "active_glt_connections"

# Controls
SET_ELECTRICAL_POWER = "set_electrical_power"
BLOCK_CHP_VIA_GLT = "block_chp_via_glt"

DEVICE_TYPES = {
    2601: "5.5kW",
    2602: "2.9kW",
}

UNIT_STATUS_MAP = {
    0: "Off",
    1: "Standby",
    2: "Running",
    3: "Waiting",
    4: "Error",
}

TYPE_OF_REQUEST_MAP = {
    0: "None",
    3: "Power",
    4: "Heat",
}

LAST_SHUTDOWN_REASON_MAP = {
    0: "Undefined",
    2: "No Request",
    3: "Error",
}

HEATING_WATER_PUMP_STATUS_MAP = {
    0: "Off",
    1: "On",
}

CONTROL_STRATEGY_MAP = {
    0: "Heat",
    1: "Power",
    2: "Heat and Power",
}

POWER_MODULATION_MAP = {
    0: "Off",
    1: "On",
}