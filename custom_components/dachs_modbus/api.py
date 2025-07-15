"""API for Senertec Dachs Modbus."""

import logging
import threading
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from .const import (
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
    SET_ELECTRICAL_POWER,
    BLOCK_CHP_VIA_GLT,
)

_LOGGER = logging.getLogger(__name__)


class DachsModbusApiClient:
    """API client for Senertec Dachs Modbus."""

    def __init__(self, host: str, port: int, glt_pin: str):
        """Initialize the API client."""
        self._host = host
        self._port = port
        self._glt_pin = glt_pin
        self._client = ModbusTcpClient(self._host, self._port)
        self._lock = threading.Lock()
        self._heartbeat_timer = None
        self._power_setpoint = 0

    def __enter__(self):
        """Connect to the Modbus device."""
        self._client.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Disconnect from the Modbus device."""
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()
        self._client.close()

    def get_data(self) -> dict[str, any]:
        """Get data from the Modbus device."""
        with self._lock:
            try:
                data = {}
                # Read all registers in one go
                result = self._client.read_input_registers(address=8000, count=84, unit=1)
                if result.isError():
                    raise ConnectionException(f"Failed to read registers: {result}")

                decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big)

                data[GLT_INTERFACE_VERSION] = decoder.decode_16bit_uint()
                data[DEVICE_TYPE] = decoder.decode_16bit_uint()
                data[SERIAL_NUMBER] = decoder.decode_string(20).rstrip(b'\x00').decode('utf-8')
                data[NOMINAL_POWER] = decoder.decode_16bit_uint()
                data[UNIT_STATUS] = decoder.decode_16bit_uint()
                data[ELECTRICAL_POWER] = decoder.decode_16bit_int() / 10
                data[TYPE_OF_REQUEST] = decoder.decode_16bit_int()
                data[RUNTIME_SINCE_LAST_START] = decoder.decode_8bit_uint() / 10
                data[LAST_SHUTDOWN_REASON] = decoder.decode_16bit_uint()
                data[HEATING_WATER_PUMP_STATUS] = decoder.decode_16bit_uint()
                data[CHP_OUTLET_TEMPERATURE] = decoder.decode_16bit_uint() / 10
                data[CHP_INLET_TEMPERATURE] = decoder.decode_16bit_uint() / 10
                data[CONTROL_STRATEGY] = decoder.decode_16bit_uint()
                data[MINIMUM_RUNTIME] = decoder.decode_8bit_uint()
                data[MAX_INLET_TEMPERATURE] = decoder.decode_16bit_int() / 10
                data[POWER_MODULATION] = decoder.decode_16bit_uint()
                data[POWER_LEVEL] = decoder.decode_8bit_uint()
                data[MODULE_TYPE_DEFINITION] = decoder.decode_16bit_uint()
                data[TOTAL_OPERATING_HOURS] = decoder.decode_32bit_uint()
                data[TOTAL_STARTS] = decoder.decode_32bit_uint()
                data[GENERATED_ELECTRICAL_ENERGY] = decoder.decode_32bit_uint() / 10
                data[GENERATED_THERMAL_ENERGY] = decoder.decode_32bit_uint() / 10
                data[OPERATING_HOURS_POWER_LEVEL_1] = decoder.decode_32bit_uint()
                data[OPERATING_HOURS_POWER_LEVEL_2] = decoder.decode_32bit_uint()
                data[OPERATING_HOURS_POWER_LEVEL_3] = decoder.decode_32bit_uint()
                data[OUTSIDE_TEMPERATURE] = decoder.decode_16bit_int() / 10
                data[BUFFER_TEMPERATURE_T1] = decoder.decode_16bit_int() / 10
                data[BUFFER_TEMPERATURE_T2] = decoder.decode_16bit_int() / 10
                data[BUFFER_TEMPERATURE_T3] = decoder.decode_16bit_int() / 10
                data[BUFFER_TEMPERATURE_T4] = decoder.decode_16bit_int() / 10
                decoder.skip_bytes(20) # Skip to 8056
                data[CURRENT_DISCHARGE_POWER] = decoder.decode_16bit_uint()

                return data
            except ConnectionException as e:
                _LOGGER.error("Failed to connect to Modbus device: %s", e)
                raise

    def _send_pin(self):
        """Send the GLT PIN to the device."""
        try:
            self._client.write_register(address=8300, value=int(self._glt_pin), unit=1)
        except ConnectionException as e:
            _LOGGER.error("Failed to send GLT PIN: %s", e)
            raise

    def set_electrical_power(self, power: int):
        """Set the electrical power setpoint."""
        with self._lock:
            self._send_pin()
            self._power_setpoint = power
            self._client.write_register(address=8301, value=power, unit=1)
            self._start_heartbeat()

    def set_block_chp(self, block: bool):
        """Block or unblock the CHP."""
        with self._lock:
            self._send_pin()
            self._client.write_register(address=8302, value=1 if block else 0, unit=1)

    def _start_heartbeat(self):
        """Start the heartbeat timer."""
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()
        self._heartbeat_timer = threading.Timer(300, self._heartbeat)
        self._heartbeat_timer.start()

    def _heartbeat(self):
        """Send the heartbeat to the device."""
        with self._lock:
            if self._power_setpoint > 0:
                self.set_electrical_power(self._power_setpoint)
