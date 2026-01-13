from types import TracebackType
from typing import Optional, final

from loguru import logger
from pydantic import BaseModel

from horiba_sdk.communication import AbstractCommunicator, Response

from ...core.trigger_input_polarity import TriggerInputPolarity
from ...icl_error import AbstractErrorDB
from .abstract_device import AbstractDevice


class BaseResults(BaseModel):
    pass


# Define a model for the saq3_getAvailableData results
class Signal(BaseModel):
    unit: str
    value: float


class DataPoint(BaseModel):
    currentSignal: Signal
    elapsedTime: int
    eventMarker: bool
    overscaleCurrentChannel: bool
    overscaleVoltageChannel: bool
    pmtSignal: Signal
    pointNumber: int
    ppdSignal: Signal
    voltageSignal: Signal


class AvailableDataResults(BaseModel):
    data: list[DataPoint]


class AcqSetResults(BaseResults):
    scanCount: int
    timeStep: float
    integrationTime: float
    externalParam: int


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
        is_open: bool = response.results['open']
        return is_open

    async def is_busy(self) -> bool:
        """
        Check if the device is busy.

        Returns:
            bool: True if the device is busy, False otherwise.
        """
        response: Response = await self._execute_command('saq3_isBusy', {'index': self._id})
        is_busy: bool = response.results['isBusy']
        return is_busy

    async def get_serial_number(self) -> str:
        """
        Retrieve the serial number of the SpectrAcq3 device.

        This method sends a command to the device to fetch its serial number. Knowing the serial number is essential
        for device identification and tracking, especially in environments with multiple devices.

        Returns:
            str: The serial number of the device.
        """
        response: Response = await self._execute_command('saq3_getSerialNumber', {'index': self._id})
        serial_number: str = response.results['serialNumber']
        return serial_number

    async def get_firmware_version(self) -> str:
        """
        Get the firmware version of the device.

        This method sends a command to the device to fetch its firmware version.

        Returns:
            str: The firmware version of the device.
        """
        response: Response = await self._execute_command('saq3_getFirmwareVersion', {'index': self._id})
        firmware_version: str = response.results['firmwareVersion']
        return firmware_version

    async def get_fpga_version(self) -> str:
        """
        Get the FPGA version of the device.

        This method sends a command to the device to fetch its FPGA version.

        Returns:
            str: The FPGA version of the device.
        """
        response: Response = await self._execute_command('saq3_getFPGAVersion', {'index': self._id})
        fpga_version: str = response.results['FpgaVersion']
        return fpga_version

    async def get_board_revision(self) -> str:
        """
        Get the board revision of the device.

        This method sends a command to the device to fetch its board revision.

        Returns:
            str: The board revision of the device.
        """
        response: Response = await self._execute_command('saq3_getBoardRevision', {'index': self._id})
        board_revision: str = response.results['boardRevision']
        return board_revision

    async def set_hv_bias_voltage(self, bias_voltage: int) -> None:
        """
        Set the high bias voltage.

        This method sends a command to the device to set the high bias voltage.

        Args:
            bias_voltage (int): The high bias voltage in volts.
        """
        await self._execute_command('saq3_setHVBiasVoltage', {'index': self._id, 'biasVoltage': bias_voltage})

    async def get_hv_bias_voltage(self) -> int:
        """
        Get the high bias voltage that was previously set.

        This method sends a command to the device to fetch the high bias voltage.

        Returns:
            int: The high bias voltage in volts.
        """
        response: Response = await self._execute_command('saq3_getHVBiasVoltage', {'index': self._id})
        hv_bias_voltage: int = response.results['biasVoltage']
        return hv_bias_voltage

    async def get_max_hv_voltage_allowed(self) -> int:
        """
        Get the maximum high bias voltage allowed.

        This method sends a command to the device to fetch the maximum high bias voltage allowed.

        Returns:
            int: The maximum high bias voltage in volts.
        """
        response: Response = await self._execute_command('saq3_getMaxHVVoltageAllowed', {'index': self._id})
        max_hv_voltage: int = response.results['biasVoltage']
        return max_hv_voltage

    async def set_acq_set(self, scan_count: int, time_step: float, integration_time: float, 
                          external_param: int) -> None:
        """
        Define the acquisition set parameters.

        This method sends a command to the device to define the acquisition set parameters.

        Args:
            scan_count (int): Number of acquisitions to perform.
            time_step (float): Time interval in seconds between acquisitions.
            integration_time (float): Integration time in seconds.
            external_param (int): User defined value.
        """
        await self._execute_command(
            'saq3_setAcqSet',
            {
                'index': self._id,
                'scanCount': scan_count,
                'timeStep': time_step,
                'integrationTime': integration_time,
                'externalParam': external_param,
            },
        )

    async def get_acq_set(self) -> dict:
        """
        Get the acquisition set parameters.

        This method sends a command to the device to fetch the acquisition set parameters.

        Returns:
            dict: The acquisition set parameters.
        """
        response: Response = await self._execute_command('saq3_getAcqSet', {'index': self._id})
        acq_set: dict = response.results
        return acq_set

    async def acq_start(self, trigger: int) -> None:
        """
        Start the acquisition.

        Trigger Modes:
        >| Mode  | description   |
        >|1| 1st data started on Start command, all subsequent data acquired based on interval time|
        >|2| 1st data started by Trigger after start Command, all subsequent data acquired based on interval time |
        >|3| Each data acquisition waits for Trigger

        Args:
            trigger (int): Integer indicating the trigger mode.
        """
        await self._execute_command('saq3_acqStart', {'index': self._id, 'trigger': trigger})

    async def acq_stop(self) -> None:
        """
        Stop the current acquisition.

        This method sends a command to the device to stop the current acquisition.
        """
        await self._execute_command('saq3_acqStop', {'index': self._id})

    async def acq_pause(self) -> None:
        """
        Pause the active acquisition.

        This method sends a command to the device to pause the active acquisition.
        """
        await self._execute_command('saq3_acqPause', {'index': self._id})

    async def acq_continue(self) -> None:
        """
        Continue a paused acquisition.

        This method sends a command to the device to continue a paused acquisition.
        """
        await self._execute_command('saq3_acqContinue', {'index': self._id})

    async def is_data_available(self) -> bool:
        """
        Check whether the acquired data is available.

        This method sends a command to the device to check if the acquired data is available.

        Returns:
            bool: True if data is available, False otherwise.
        """
        response: Response = await self._execute_command('saq3_isDataAvailable', {'index': self._id})
        is_data_available: bool = response.results['isDataAvailable']
        return is_data_available

    async def get_available_data(self, channels) -> AvailableDataResults:
        """
        Retrieve the acquired data that is available so far.

        This method sends a command to the device to retrieve the acquired data.

        Returns:
            list: The acquired data.
        """
        response: Response = await self._execute_command('saq3_getAvailableData', {'index': self._id, 
                                                                                   'channels': channels})
        available_data: AvailableDataResults = response.results['data']
        return available_data

    async def force_trigger(self) -> None:
        """
        Force a software trigger.

        This method sends a command to the device to force a software trigger.
        """
        await self._execute_command('saq3_forceTrigger', {'index': self._id})

    async def set_trigger_in_polarity(self, polarity: TriggerInputPolarity) -> None:
        """
        Set the input trigger polarity.

        Args:
            polarity (TriggerInputPolarity): Input trigger polarity (ACTIVE_LOW or ACTIVE_HIGH).
        """
        await self._execute_command('saq3_setTriggerInPolarity', {'index': self._id, 'polarity': polarity.value})

    async def get_trigger_in_polarity(self) -> int:
        """
        Get the input trigger polarity.

        Returns:
            int: Input trigger polarity (0: Active Low, 1: Active High).
        """
        response: Response = await self._execute_command('saq3_getTriggerInPolarity', {'index': self._id})
        polarity: int = response.results['polarity']
        return polarity

    async def set_in_trigger_mode(self, mode: int) -> None:
        """
        Set the hardware trigger pin mode.

        This method sends a command to the device to set the hardware trigger pin mode.

        Args:
            mode (int): Mode of hardware trigger pin.
        """
        await self._execute_command('saq3_setInTriggerMode', {'index': self._id, 'mode': mode})

    async def get_trigger_mode(self) -> dict:
        """
        Get the trigger mode.

        This method sends a command to the device to fetch the trigger mode.

        Returns:
            dict: The trigger mode settings.
        """
        response: Response = await self._execute_command('saq3_getInTriggerMode', {'index': self._id})
        trigger_mode: dict = response.results
        return trigger_mode

    async def get_last_error(self) -> str:
        """
        Get the last error.

        This method sends a command to the device to fetch the last error.

        Returns:
            str: The last error message.
        """
        response: Response = await self._execute_command('saq3_getLastError', {'index': self._id})
        last_error: str = response.results['error']
        return last_error

    async def get_error_log(self) -> list[str]:
        """
        Get the error log.

        This method sends a command to the device to fetch the error log.

        Returns:
            str: The error log.
        """
        response: Response = await self._execute_command('saq3_getErrorLog', {'index': self._id})
        error_log: list[str] = response.results['errors']
        return error_log

    async def clear_error_log(self) -> None:
        """
        Clear all the errors in the log.

        This method sends a command to the device to clear the error log.
        """
        await self._execute_command('saq3_clearErrorLog', {'index': self._id})
