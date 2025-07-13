"""API for Senertec Dachs Modbus."""

import logging

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

_LOGGER = logging.getLogger(__name__)


class DachsModbusApiClient:
    """API client for Senertec Dachs Modbus."""

    def __init__(self, host: str, port: int):
        """Initialize the API client."""
        self._host = host
        self._port = port
        self._client = ModbusTcpClient(host, port)

    def __enter__(self):
        """Connect to the Modbus device."""
        self._client.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Disconnect from the Modbus device."""
        self._client.close()

    def get_data(self) -> dict[str, any]:
        """Get data from the Modbus device."""
        try:
            # This is where you would read the registers from the Modbus device.
            # The following is just an example.
            # You will need to know the register addresses for the data you want to read.
            # result = self._client.read_holding_registers(address=0, count=10, unit=1)
            # if result.isError():
            #     raise ConnectionException(f"Failed to read registers: {result}")
            #
            # data = {
            #     "example_value": result.registers[0],
            # }
            # return data
            return {}  # Return empty dict for now
        except ConnectionException as e:
            _LOGGER.error("Failed to connect to Modbus device: %s", e)
            raise
