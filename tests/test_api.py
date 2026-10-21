"""Tests for the Dachs GLT API client (no Home Assistant needed)."""

import struct
import threading
from unittest.mock import patch

import pytest

from custom_components.dachs_modbus import api
from custom_components.dachs_modbus.api import (
    READ_COUNT,
    REG_BLOCK_CHP,
    REG_GLT_PIN,
    REG_SET_ELECTRICAL_POWER,
    DachsModbusApiClient,
    decode_registers,
)
from custom_components.dachs_modbus.const import (
    BLOCK_CHP_VIA_GLT,
    BUFFER_TEMPERATURE_T4,
    CURRENT_DISCHARGE_POWER,
    DEVICE_TYPE,
    ELECTRICAL_POWER,
    OUTSIDE_TEMPERATURE,
    RUNTIME_SINCE_LAST_START,
    SERIAL_NUMBER,
    SET_ELECTRICAL_POWER,
    TOTAL_STARTS,
)


class Result:
    def __init__(self, registers=None, error=False):
        self.registers = registers or []
        self._error = error

    def isError(self):  # noqa: N802 - pymodbus API
        return self._error


class FakeModbus:
    """Records writes; serves a fixed register block."""

    def __init__(self, registers=None, fail_writes=False):
        self.registers = registers if registers is not None else [0] * READ_COUNT
        self.fail_writes = fail_writes
        self.writes = []
        self.closed = False

    def read_input_registers(self, address, count):
        assert (address, count) == (8000, READ_COUNT)
        return Result(self.registers)

    def write_register(self, address, value):
        self.writes.append((address, value))
        return Result(error=self.fail_writes)

    def close(self):
        self.closed = True


def block(**fields):
    regs = [0] * READ_COUNT
    for off, value in fields.items():
        regs[int(off[1:])] = value
    return regs


def test_decode_aligns_every_field_on_its_own_register():
    regs = block(
        r1=2601, r14=55, r16=123, r29=0, r30=4242, r41=0xFFEC, r45=612, r56=777
    )
    serial = b"DACHS-0815".ljust(20, b"\x00")
    for i in range(10):
        regs[2 + i] = struct.unpack(">H", serial[2 * i : 2 * i + 2])[0]
    data = decode_registers(regs)
    assert data[DEVICE_TYPE] == 2601
    assert data[SERIAL_NUMBER] == "DACHS-0815"
    assert data[ELECTRICAL_POWER] == 5.5
    # Formerly decoded as a single byte, which shifted every later field.
    assert data[RUNTIME_SINCE_LAST_START] == 12.3
    assert data[TOTAL_STARTS] == 4242
    assert data[OUTSIDE_TEMPERATURE] == -2.0
    assert data[BUFFER_TEMPERATURE_T4] == 61.2
    assert data[CURRENT_DISCHARGE_POWER] == 777


def test_decode_rejects_short_block():
    with pytest.raises(ValueError):
        decode_registers([0] * 10)


def test_get_data_includes_assumed_control_state():
    client = DachsModbusApiClient("h", 502, "1234", client=FakeModbus())
    data = client.get_data()
    assert data[SET_ELECTRICAL_POWER] == 0
    assert data[BLOCK_CHP_VIA_GLT] is None
    client.set_block_chp(True)
    assert client.get_data()[BLOCK_CHP_VIA_GLT] is True


def test_read_error_raises():
    fake = FakeModbus()
    fake.read_input_registers = lambda address, count: Result(error=True)
    client = DachsModbusApiClient("h", 502, "1234", client=fake)
    with pytest.raises(Exception):
        client.get_data()


def test_writes_send_pin_first():
    fake = FakeModbus()
    client = DachsModbusApiClient("h", 502, "1234", client=fake)
    client.set_block_chp(False)
    assert fake.writes == [(REG_GLT_PIN, 1234), (REG_BLOCK_CHP, 0)]


def test_failed_write_raises_and_keeps_previous_state():
    fake = FakeModbus(fail_writes=True)
    client = DachsModbusApiClient("h", 502, "1234", client=fake)
    with pytest.raises(Exception):
        client.set_block_chp(True)
    assert client.get_data()[BLOCK_CHP_VIA_GLT] is None


def test_setpoint_schedules_heartbeat_and_zero_cancels_it():
    fake = FakeModbus()
    client = DachsModbusApiClient("h", 502, "1234", client=fake)
    with patch.object(api.threading, "Timer") as timer:
        client.set_electrical_power(5500)
        timer.assert_called_once()
        assert (REG_SET_ELECTRICAL_POWER, 5500) in fake.writes
        client.set_electrical_power(0)
        timer.return_value.cancel.assert_called()
        assert timer.call_count == 1  # no new heartbeat for a 0 setpoint
    assert client.get_data()[SET_ELECTRICAL_POWER] == 0


def test_heartbeat_does_not_deadlock():
    """The heartbeat re-sends the setpoint while holding the lock."""
    fake = FakeModbus()
    client = DachsModbusApiClient("h", 502, "1234", client=fake)
    with patch.object(api.threading, "Timer"):
        client.set_electrical_power(3000)
        fake.writes.clear()
        t = threading.Thread(target=client._heartbeat)
        t.start()
        t.join(timeout=2)
    assert not t.is_alive(), "heartbeat deadlocked"
    assert (REG_SET_ELECTRICAL_POWER, 3000) in fake.writes


def test_negative_setpoint_rejected():
    client = DachsModbusApiClient("h", 502, "1234", client=FakeModbus())
    with pytest.raises(ValueError):
        client.set_electrical_power(-1)


def test_close_stops_heartbeat_and_connection():
    fake = FakeModbus()
    client = DachsModbusApiClient("h", 502, "1234", client=fake)
    with patch.object(api.threading, "Timer") as timer:
        client.set_electrical_power(1000)
        client.close()
        timer.return_value.cancel.assert_called()
    assert fake.closed
