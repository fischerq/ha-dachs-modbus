"""API for Senertec Dachs Modbus (GLT interface)."""

import logging
import struct
import threading

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException

from .const import (
    GLT_INTERFACE_VERSION,
    DEVICE_TYPE,
    SERIAL_NUMBER,
    NOMINAL_POWER,
    UNIT_STATUS,
    ELECTRICAL_POWER,
    TYPE_OF_REQUEST,
    RUNTIME_SINCE_LAST_START,
    LAST_SHUTDOWN_REASON,
    HEATING_WATER_PUMP_STATUS,
    CHP_OUTLET_TEMPERATURE,
    CHP_INLET_TEMPERATURE,
    CONTROL_STRATEGY,
    MINIMUM_RUNTIME,
    MAX_INLET_TEMPERATURE,
    POWER_MODULATION,
    POWER_LEVEL,
    MODULE_TYPE_DEFINITION,
    TOTAL_OPERATING_HOURS,
    TOTAL_STARTS,
    GENERATED_ELECTRICAL_ENERGY,
    GENERATED_THERMAL_ENERGY,
    OPERATING_HOURS_POWER_LEVEL_1,
    OPERATING_HOURS_POWER_LEVEL_2,
    OPERATING_HOURS_POWER_LEVEL_3,
    OUTSIDE_TEMPERATURE,
    BUFFER_TEMPERATURE_T1,
    BUFFER_TEMPERATURE_T2,
    BUFFER_TEMPERATURE_T3,
    BUFFER_TEMPERATURE_T4,
    CURRENT_DISCHARGE_POWER,
    SET_ELECTRICAL_POWER,
    BLOCK_CHP_VIA_GLT,
)

_LOGGER = logging.getLogger(__name__)

READ_START = 8000
READ_COUNT = 57  # 8000..8056

REG_GLT_PIN = 8300
REG_SET_ELECTRICAL_POWER = 8301
REG_BLOCK_CHP = 8302

# Seconds between setpoint refreshes. The GLT drops an external power request
# that is not renewed; refresh well inside that window.
HEARTBEAT_SECONDS = 300

# (key, register offset from READ_START, type, scale divisor).
# Every value starts on its own 16-bit register: "u8" values occupy a full
# register too. Decoding them as single bytes (as earlier versions did)
# shifted every later field by a byte.
#
# NOTE: this map has not yet been checked against Senertec's GLT Modbus
# documentation or a live unit. Verify with scripts/probe.py before relying
# on the values for control.
REGISTER_MAP: tuple[tuple[str, int, str, float], ...] = (
    (GLT_INTERFACE_VERSION, 0, "u16", 1),
    (DEVICE_TYPE, 1, "u16", 1),
    (SERIAL_NUMBER, 2, "str20", 1),  # 10 registers
    (NOMINAL_POWER, 12, "u16", 1),
    (UNIT_STATUS, 13, "u16", 1),
    (ELECTRICAL_POWER, 14, "s16", 10),
    (TYPE_OF_REQUEST, 15, "s16", 1),
    (RUNTIME_SINCE_LAST_START, 16, "u16", 10),
    (LAST_SHUTDOWN_REASON, 17, "u16", 1),
    (HEATING_WATER_PUMP_STATUS, 18, "u16", 1),
    (CHP_OUTLET_TEMPERATURE, 19, "u16", 10),
    (CHP_INLET_TEMPERATURE, 20, "u16", 10),
    (CONTROL_STRATEGY, 21, "u16", 1),
    (MINIMUM_RUNTIME, 22, "u16", 1),
    (MAX_INLET_TEMPERATURE, 23, "s16", 10),
    (POWER_MODULATION, 24, "u16", 1),
    (POWER_LEVEL, 25, "u16", 1),
    (MODULE_TYPE_DEFINITION, 26, "u16", 1),
    (TOTAL_OPERATING_HOURS, 27, "u32", 1),
    (TOTAL_STARTS, 29, "u32", 1),
    (GENERATED_ELECTRICAL_ENERGY, 31, "u32", 10),
    (GENERATED_THERMAL_ENERGY, 33, "u32", 10),
    (OPERATING_HOURS_POWER_LEVEL_1, 35, "u32", 1),
    (OPERATING_HOURS_POWER_LEVEL_2, 37, "u32", 1),
    (OPERATING_HOURS_POWER_LEVEL_3, 39, "u32", 1),
    (OUTSIDE_TEMPERATURE, 41, "s16", 10),
    (BUFFER_TEMPERATURE_T1, 42, "s16", 10),
    (BUFFER_TEMPERATURE_T2, 43, "s16", 10),
    (BUFFER_TEMPERATURE_T3, 44, "s16", 10),
    (BUFFER_TEMPERATURE_T4, 45, "s16", 10),
    (CURRENT_DISCHARGE_POWER, 56, "u16", 1),
)


def decode_registers(registers: list[int]) -> dict:
    """Decode the 8000.. input-register block into a data dict (big endian)."""
    if len(registers) < READ_COUNT:
        raise ValueError(f"expected {READ_COUNT} registers, got {len(registers)}")
    data: dict = {}
    for key, off, kind, scale in REGISTER_MAP:
        if kind == "u16":
            value = registers[off]
        elif kind == "s16":
            value = struct.unpack(">h", struct.pack(">H", registers[off]))[0]
        elif kind == "u32":
            value = (registers[off] << 16) | registers[off + 1]
        elif kind == "str20":
            raw = b"".join(struct.pack(">H", r) for r in registers[off : off + 10])
            data[key] = raw.rstrip(b"\x00").decode("ascii", errors="replace").strip()
            continue
        else:  # pragma: no cover - guarded by the static map
            raise ValueError(kind)
        data[key] = value / scale if scale != 1 else value
    return data


class DachsModbusApiClient:
    """Synchronous client for the Dachs GLT; call from an executor."""

    def __init__(self, host: str, port: int, glt_pin: str, client=None):
        """Initialize the API client."""
        self._host = host
        self._port = port
        self._glt_pin = int(glt_pin)
        self._client = client or ModbusTcpClient(host, port=port)
        # Re-entrant: the heartbeat re-sends the setpoint under the same lock.
        self._lock = threading.RLock()
        self._heartbeat_timer: threading.Timer | None = None
        self._power_setpoint = 0
        self._blocked: bool | None = None

    def close(self) -> None:
        """Stop the heartbeat and close the connection."""
        with self._lock:
            if self._heartbeat_timer:
                self._heartbeat_timer.cancel()
                self._heartbeat_timer = None
            self._client.close()

    def get_data(self) -> dict:
        """Read all values; adds the last commanded (assumed) control state."""
        with self._lock:
            result = self._client.read_input_registers(
                address=READ_START, count=READ_COUNT
            )
            if result.isError():
                raise ConnectionException(f"Failed to read registers: {result}")
            data = decode_registers(result.registers)
        data[SET_ELECTRICAL_POWER] = self._power_setpoint
        data[BLOCK_CHP_VIA_GLT] = self._blocked
        return data

    def _write(self, address: int, value: int) -> None:
        result = self._client.write_register(address=address, value=value)
        if result.isError():
            raise ModbusException(f"Write {address}={value} failed: {result}")

    def _send_pin(self) -> None:
        self._write(REG_GLT_PIN, self._glt_pin)

    def set_electrical_power(self, power: int) -> None:
        """Set the electrical power setpoint (W); 0 withdraws the request."""
        if power < 0:
            raise ValueError("power must be >= 0")
        with self._lock:
            self._send_pin()
            self._write(REG_SET_ELECTRICAL_POWER, int(power))
            self._power_setpoint = int(power)
            self._schedule_heartbeat()

    def set_block_chp(self, block: bool) -> None:
        """Block (True) or release (False) the CHP via GLT."""
        with self._lock:
            self._send_pin()
            self._write(REG_BLOCK_CHP, 1 if block else 0)
            self._blocked = block

    def _schedule_heartbeat(self) -> None:
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()
            self._heartbeat_timer = None
        if self._power_setpoint > 0:
            self._heartbeat_timer = threading.Timer(HEARTBEAT_SECONDS, self._heartbeat)
            self._heartbeat_timer.daemon = True
            self._heartbeat_timer.start()

    def _heartbeat(self) -> None:
        """Renew the external power request."""
        try:
            with self._lock:
                if self._power_setpoint > 0:
                    self.set_electrical_power(self._power_setpoint)
        except Exception:  # noqa: BLE001 - timer thread: log, retry next beat
            _LOGGER.exception("Dachs heartbeat failed; retrying")
            self._schedule_heartbeat()
