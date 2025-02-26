from enum import Enum
from typing import Any

from horiba_sdk.communication import AbstractCommunicator, Response
from horiba_sdk.icl_error import AbstractErrorDB

from .abstract_device import AbstractDevice


class SpectrAcq3(AbstractDevice):
    """
    SpectrAcq3 device class.

    This class represents the SpectrAcq3 - Single Channel Detector Interface. It provides methods to open and close
    the device connection and retrieve the device's serial number. The focus is on ensuring reliable communication
    with the device and handling any potential errors gracefully.
    """

    class Status(Enum):
        """
        Enum representing the status of the SpectrAcq3 device.

        This enum is used to define the possible states of the device, which helps in managing the device's lifecycle
        and ensuring that operations are performed only when the device is in a valid state.
        """
        CLOSED = 0
        OPEN = 1

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