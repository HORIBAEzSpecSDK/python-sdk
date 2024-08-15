"""
Synchronous Device Manager Module

This Device Manager uses threads instead of asyncio
"""
import importlib.resources
import platform
import subprocess
from pathlib import Path
from subprocess import Popen
from typing import Optional, final

import psutil
from loguru import logger
from overrides import override

from horiba_sdk.communication import Command, CommunicationException, Response
from horiba_sdk.icl_error import AbstractError, AbstractErrorDB, ICLErrorDB
from horiba_sdk.sync.communication import AbstractCommunicator, WebsocketCommunicator
from horiba_sdk.sync.devices import AbstractDeviceManager, DeviceDiscovery
from horiba_sdk.sync.devices.single_devices import ChargeCoupledDevice, Monochromator


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
        self._icl_websocket_ip: str = icl_ip
        self._icl_websocket_port: str = icl_port
        self._icl_process: Optional[Popen[bytes]] = None
        self._binary_messages: bool = enable_binary_messages
        self._charge_coupled_devices: list[ChargeCoupledDevice] = []
        self._monochromators: list[Monochromator] = []

        error_list_path: Path = Path(str(importlib.resources.files('horiba_sdk.icl_error') / 'error_list.json'))
        self._icl_error_db: AbstractErrorDB = ICLErrorDB(error_list_path)

    @override
    def start(self) -> None:
        if self._start_icl:
            self.start_icl()

        self._icl_communicator.register_binary_message_callback(self._binary_message_callback)
        self._icl_communicator.open()

        icl_info: Response = self._icl_communicator.request_with_response(Command('icl_info', {}))
        logger.info(f'ICL info: {icl_info.results}')

        if self._binary_messages:
            self._enable_binary_messages()

        self.discover_devices()

    @override
    def stop(self) -> None:
        if self._start_icl:
            self.stop_icl()
            return

        if self._icl_communicator.opened():
            self._icl_communicator.close()

    def start_icl(self) -> None:
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
            try:
                self._icl_process = subprocess.Popen([r'C:\Program Files\HORIBA Scientific\SDK\icl.exe'])
            except subprocess.CalledProcessError as error:
                logger.error('Failed to start ICL software.')
                raise Exception('Failed to start ICL software') from error

    def _enable_binary_messages(self) -> None:
        bin_mode_command: Command = Command('icl_binMode', {'mode': 'all'})
        response: Response = self._icl_communicator.request_with_response(bin_mode_command)

        if response.errors:
            self._handle_errors(response.errors)

    def _handle_errors(self, errors: list[str]) -> None:
        for error in errors:
            icl_error: AbstractError = self._icl_error_db.error_from(error)
            icl_error.log()
            # TODO: [saga] only throw depending on the log level, tbd
            raise Exception(f'Error from the ICL: {icl_error.message()}')

    def stop_icl(self) -> None:
        """
        Stops the communication and cleans up resources.
        """
        logger.info('Requesting shutdown of ICL...')

        if not self._icl_communicator.opened():
            self._icl_communicator.open()

        try:
            info_command: Command = Command('icl_info', {})
            response: Response = self._icl_communicator.request_with_response(info_command)

            logger.info(f'ICL info: {response.results}')
            shutdown_command: Command = Command('icl_shutdown', {})
            # _response: Response = self._icl_communicator.request_with_response(shutdown_command, timeout=10)
            _response: Response = self._icl_communicator.request_with_response(shutdown_command)
        except CommunicationException as e:
            logger.debug(f'CommunicationException: {e.message}')

        if self._icl_communicator.opened():
            self._icl_communicator.close()

        if self._icl_process is not None:
            self._icl_process.terminate()
        icl_running = 'icl.exe' in (p.name() for p in psutil.process_iter())
        if icl_running:
            raise Exception('Failed to shutdown ICL software.')

        logger.info('icl_shutdown command sent')

    def _format_icl_binary_to_string(self, message: bytes) -> str:
        return ' '.join(format(byte, '02x') for byte in message[::-1])

    def _binary_message_callback(self, message: bytes) -> None:
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
    def discover_devices(self, error_on_no_device: bool = False) -> None:
        """
        Discovers the connected devices and saves them internally.

        Args:
            error_on_no_device (bool): If True, an exception is raised if no device is connected.
        """
        device_discovery: DeviceDiscovery = DeviceDiscovery(self._icl_communicator, self._icl_error_db)
        device_discovery.execute(error_on_no_device)
        self._charge_coupled_devices = device_discovery.charge_coupled_devices()
        self._monochromators = device_discovery.monochromators()

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
