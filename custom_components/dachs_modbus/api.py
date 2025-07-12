"""API client for the Modbus TCP device."""

import logging
import aiohttp
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException


_LOGGER = logging.getLogger(__name__)


class ModbusTcpApiClientError(Exception):
    """Base exception for Modbus TCP API."""


class ModbusTcpApiClient:
    """API client for the Modbus TCP device."""

    def __init__(self, host: str, port: int):
        """
        Initialize the Modbus TCP client.

        Args:
            host (str): The hostname or IP address of the Modbus TCP device.
            port (int): The port of the Modbus TCP device.
        """
        self._client = AsyncModbusTcpClient(host, port)

    async def connect(self):
        """Connect to the Modbus TCP device."""
        _LOGGER.debug("Connecting to Modbus TCP device at %s:%s", self._client.host, self._client.port)
        try:
            await self._client.connect()
            _LOGGER.debug("Connected to Modbus TCP device.")
            return True
        except ModbusException as err:
            _LOGGER.error("Error connecting to Modbus TCP device: %s", err)
            return False

    async def disconnect(self):
        """Disconnect from the Modbus TCP device."""
        if self._client.is_connected():
            _LOGGER.debug("Disconnecting from Modbus TCP device.")
            self._client.close()
            _LOGGER.debug("Disconnected from Modbus TCP device.")

    async def read_holding_registers(self, address: int, count: int, slave_id: int = 0):
        """Read holding registers from the Modbus TCP device."""
        _LOGGER.debug("Reading holding registers: address=%s, count=%s, slave_id=%s", address, count, slave_id)
        try:
            response = await self._client.read_holding_registers(address, count, slave_id)
            if response.is_exception():
                _LOGGER.error("Modbus exception reading holding registers: %s", response)
                raise ModbusTcpApiClientError(f"Modbus exception: {response}")
            _LOGGER.debug("Successfully read holding registers: %s", response.registers)
            return response.registers
        except ModbusException as err:
            _LOGGER.error("Error reading holding registers: %s", err)
            raise ModbusTcpApiClientError(f"Modbus communication error: {err}") from err

    async def get_daily_rewards(self):
        """Fetch daily rewards from Braiins Pool API. Not parsed yet."""
        url = API_URL_DAILY_REWARDS.format(DEFAULT_COIN)
        return await self._request(url)

    async def get_daily_hashrate(self, group="user", coin=DEFAULT_COIN):
        """Fetch daily hashrate from Braiins Pool API. Not parsed yet."""
        url = API_URL_DAILY_HASHRATE.format(group, coin)
        return await self._request(url)

    async def get_block_rewards(self, from_date: str, to_date: str, coin=DEFAULT_COIN):
        """Fetch block rewards from Braiins Pool API. Not parsed yet."""
        url = API_URL_BLOCK_REWARDS.format(coin, from_date, to_date)
        return await self._request(url)

    async def get_workers(self, coin=DEFAULT_COIN):
        """Fetch worker data from Braiins Pool API. Not parsed yet."""
        url = API_URL_WORKERS.format(coin)
        return await self._request(url)

    async def get_payouts(self, from_date: str, to_date: str, coin=DEFAULT_COIN):
        """Fetch payouts data from Braiins Pool API. Not parsed yet."""
        url = API_URL_PAYOUTS.format(coin, from_date, to_date)
        return await self._request(url)
