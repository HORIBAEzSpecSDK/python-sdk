"""
Device Manager Module

This module provides the DeviceManager class, responsible for managing the lifecycle and interactions with devices.

Import Structure Explanation:
-----------------------------
Due to the interdependence between the AbstractDevice class and the DeviceManager class, we face a potential circular
import issue. Specifically, the AbstractDevice class needs knowledge about the DeviceManager, and vice versa.

To handle this challenge while still allowing type checking tools like mypy to function correctly, we've made use of
Python's TYPE_CHECKING constant available in the `typing` module. This constant is `True` only when type checking is
performed, and not during runtime. This ensures that:

1. At runtime, there's no circular import, as the import statement within the TYPE_CHECKING block is effectively
   ignored.

2. During type checking (like when running mypy), the import statement is executed, allowing mypy to recognize and
   validate types.

Therefore, the `if TYPE_CHECKING:` block is a solution to maintain clean architecture while still benefiting from type
checking capabilities.

Notes:
------
The forward declaration method ("ClassName") is used for type hints within the module to further prevent any runtime
circular dependencies.

For more details on the TYPE_CHECKING constant and its usage, refer to:
https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING
"""

import asyncio
import importlib.resources
import platform
from pathlib import Path
from typing import Optional, final

import psutil
from loguru import logger
from overrides import override

from horiba_sdk.communication import (
    AbstractCommunicator,
    Command,
    CommunicationException,
    Response,
    WebsocketCommunicator,
)
from horiba_sdk.devices import AbstractDeviceManager
from horiba_sdk.devices.ccd_discovery import ChargeCoupledDevicesDiscovery
from horiba_sdk.devices.monochromator_discovery import MonochromatorsDiscovery
from horiba_sdk.devices.single_devices import ChargeCoupledDevice, Monochromator
from horiba_sdk.icl_error import AbstractError, AbstractErrorDB, ICLErrorDB


@final
class DeviceManager(AbstractDeviceManager):
    """
    DeviceManager class manages the lifecycle and interactions with devices.
    """

    def __init__(
        self,
        start_icl: bool = True,
        icl_ip: str = '127.0.0.1',
        icl_port: str = '25010',
        enable_binary_messages: bool = True,
    ):
        """
        Initializes the DeviceManager with the specified communicator class.

        Args:
            start_icl (bool) = True: If True, the ICL software is started and communication is established.
            icl_ip (str) = '127.0.0.1': websocket IP
            icl_port (str) = '25010': websocket port
            enable_binary_messages (bool) = True: If True, binary messages are enabled.
        """
        super().__init__()
        self._start_icl = start_icl
        self._icl_communicator: WebsocketCommunicator = WebsocketCommunicator('ws://' + icl_ip + ':' + str(icl_port))
        self._icl_communicator.register_binary_message_callback(self._binary_message_callback)
        self._icl_websocket_ip: str = icl_ip
        self._icl_websocket_port: str = icl_port
        self._icl_process: Optional[asyncio.subprocess.Process] = None
        self._binary_messages: bool = enable_binary_messages
        self._charge_coupled_devices: list[ChargeCoupledDevice] = []
        self._monochromators: list[Monochromator] = []

        error_list_path: Path = Path(str(importlib.resources.files('horiba_sdk.icl_error') / 'error_list.json'))
        self._icl_error_db: AbstractErrorDB = ICLErrorDB(error_list_path)

    @override
    async def start(self) -> None:
        if self._start_icl:
            await self.start_icl()

        await self._icl_communicator.open()

        icl_info: Response = await self._icl_communicator.request_with_response(Command('icl_info', {}))
        logger.info(f'ICL info: {icl_info.results}')

        if self._binary_messages:
            await self._enable_binary_messages()

        await self.discover_devices()

    @override
    async def stop(self) -> None:
        if self._start_icl:
            await self.stop_icl()
            return

        if self._icl_communicator.opened():
            await self._icl_communicator.close()

    async def start_icl(self) -> None:
        """
        Starts the ICL software and establishes communication.
        """
        logger.info('Starting ICL software...')
        # try:
        if platform.system() != 'Windows':
            logger.info('Only Windows is supported for ICL software. Skip starting of ICL...')
            return

        icl_running = 'icl.exe' in (p.name() for p in psutil.process_iter())
        if not icl_running:
            logger.info('icl not running, starting it...')
            # subprocess.Popen([r'C:\Program Files\HORIBA Scientific\SDK\icl.exe'])
            self._icl_process = await asyncio.create_subprocess_exec(r'C:\Program Files\HORIBA Scientific\SDK\icl.exe')
        # except subprocess.CalledProcessError:
        #    logger.error('Failed to start ICL software.')
        # TODO: [saga] is this the best way handle exceptions?
        # except Exception as e:  # pylint: disable=broad-exception-caught
        #     logger.error('Unexpected error: %s', e)

    async def _enable_binary_messages(self) -> None:
        bin_mode_command: Command = Command('icl_binMode', {'mode': 'all'})
        response: Response = await self._icl_communicator.request_with_response(bin_mode_command)

        if response.errors:
            self._handle_errors(response.errors)

    def _handle_errors(self, errors: list[str]) -> None:
        for error in errors:
            icl_error: AbstractError = self._icl_error_db.error_from(error)
            icl_error.log()
            # TODO: [saga] only throw depending on the log level, tbd
            raise Exception(f'Error from the ICL: {icl_error.message()}')

    async def stop_icl(self) -> None:
        """
        Stops the communication and cleans up resources.
        """
        logger.info('Requesting shutdown of ICL...')

        if not self._icl_communicator.opened():
            await self._icl_communicator.open()

        try:
            info_command: Command = Command('icl_info', {})
            response: Response = await self._icl_communicator.request_with_response(info_command)

            logger.info(f'ICL info: {response.results}')
            shutdown_command: Command = Command('icl_shutdown', {})
            _response: Response = await self._icl_communicator.request_with_response(shutdown_command, timeout=10)
        except CommunicationException as e:
            logger.debug(f'CommunicationException: {e.message}')

        if self._icl_communicator.opened():
            await self._icl_communicator.close()

        if self._icl_process is not None:
            await self._icl_process.wait()
        icl_running = 'icl.exe' in (p.name() for p in psutil.process_iter())
        if icl_running:
            raise Exception('Failed to shutdown ICL software.')

        logger.info('icl_shutdown command sent')

    def _format_icl_binary_to_string(self, message: bytes) -> str:
        return ' '.join(format(byte, '02x') for byte in message[::-1])

    async def _binary_message_callback(self, message: bytes) -> None:
        # hex_data = ' '.join(format(byte, '02x') for byte in message)
        # if len(message) < 18:
        #     logger.warning(f'binary message not valid: {len(message)} < 16')
        # logger.info(f'Received binary message: {hex_data}')
        # logger.info(f'magic number: {self._format_icl_binary_to_string(message[:2])}')
        # logger.info(f'message type: {self._format_icl_binary_to_string(message[2:4])}')
        # logger.info(f'element type: {self._format_icl_binary_to_string(message[4:6])}')
        # logger.info(f'element count: {self._format_icl_binary_to_string(message[6:10])}')
        # logger.info(f'tag 1: {self._format_icl_binary_to_string(message[10:12])}')
        # logger.info(f'tag 2: {self._format_icl_binary_to_string(message[12:14])}')
        # logger.info(f'tag 3: {self._format_icl_binary_to_string(message[14:16])}')
        # logger.info(f'tag 4: {self._format_icl_binary_to_string(message[16:18])}')
        # logger.info(f'payload: {self._format_icl_binary_to_string(message[18:])}')
        # logger.info(f'payload as string: {str(message[18:])}')
        pass

    @override
    async def discover_devices(self, error_on_no_device: bool = False) -> None:
        """
        Discovers the connected devices and saves them internally.

        Args:
            error_on_no_device (bool): If True, an exception is raised if no device is connected.
        """
        ccds_discovery: ChargeCoupledDevicesDiscovery = ChargeCoupledDevicesDiscovery(
            self._icl_communicator, self._icl_error_db
        )
        await ccds_discovery.execute(error_on_no_device)
        self._charge_coupled_devices = ccds_discovery.charge_coupled_devices()

        monochromators_discovery: MonochromatorsDiscovery = MonochromatorsDiscovery(
            self._icl_communicator, self._icl_error_db
        )
        await monochromators_discovery.execute(error_on_no_device)
        self._monochromators = monochromators_discovery.monochromators()

    @property
    @override
    def communicator(self) -> AbstractCommunicator:
        """
        Getter method for the communicator attribute.

        Returns:
            horiba_sdk.communication.AbstractCommunicator: Returns a new communicator instance.
        """
        return self._icl_communicator

    @property
    @override
    def monochromators(self) -> list[Monochromator]:
        """
        The detected monochromators, should be called after :meth:`discover_devices`

        Returns:
            List[Monochromator]: The detected monochromators
        """
        return self._monochromators

    @property
    @override
    def charge_coupled_devices(self) -> list[ChargeCoupledDevice]:
        """
        The detected CCDs, should be called after :meth:`discover_devices`

        Returns:
            List[ChargeCoupledDevice]: The detected CCDS.
        """
        return self._charge_coupled_devices
