from types import TracebackType
from typing import Optional, final

from loguru import logger

from horiba_sdk.communication import AbstractCommunicator, Response

from ...icl_error import AbstractErrorDB
from .abstract_device import AbstractDevice


@final
class SpectrAcq3(AbstractDevice):
    """
    SpectrAcq3 device class.

    This class represents the SpectrAcq3 - Single Channel Detector Interface. It provides methods to open and close
    the device connection and retrieve the device's serial number. The focus is on ensuring reliable communication
    with the device and handling any potential errors gracefully.
    """

    def __init__(self, device_id: int, communicator: AbstractCommunicator, error_db: AbstractErrorDB) -> None:
        super().__init__(device_id, communicator, error_db)

    async def __aenter__(self) -> 'SpectrAcq3':
        await self.open()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException], exc_value: BaseException, traceback: Optional[TracebackType]
    ) -> None:
        is_open = await self.is_open()
        if not is_open:
            logger.debug('SpectrAcq3 is already closed')
            return

        await self.close()

    async def open(self) -> None:
        """
        Open a connection to the SpectrAcq3 device.

        This method sends a command to the device to establish a connection. It is crucial to ensure that the device
        is ready for communication before attempting any operations, to prevent errors and data loss.
        """
        await self._execute_command('saq3_open', {'index': self._id})

    async def close(self) -> None:
        """
        Close the connection to the SpectrAcq3 device.

        This method sends a command to safely terminate the connection with the device. Properly closing the connection
        helps in freeing up resources and maintaining the device's integrity for future operations.
        """
        await self._execute_command('saq3_close', {'index': self._id})

    async def is_open(self) -> bool:
        """
        Check if the connection to the SpectrAcq3 device is open.

        This method checks the status of the device connection to determine if it is open or closed. It is useful for
        verifying the device's state before performing any operations that require an active connection.

        Returns:
            bool: True if the connection is open, False otherwise.
        """
        response: Response = await self._execute_command('saq3_isOpen', {'index': self._id})
        return response.results['open']

    async def get_serial_number(self) -> str:
        """
        Retrieve the serial number of the SpectrAcq3 device.

        This method sends a command to the device to fetch its serial number. Knowing the serial number is essential
        for device identification and tracking, especially in environments with multiple devices.

        Returns:
            str: The serial number of the device.
        """
        response: Response = await self._execute_command('saq3_getSerialNumber', {'index': self._id})
        return response.results['serialNumber']
