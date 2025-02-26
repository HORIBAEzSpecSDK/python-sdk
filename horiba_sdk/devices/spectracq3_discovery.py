from typing import Any, final

from loguru import logger
from overrides import override

from horiba_sdk.communication import AbstractCommunicator, Command, Response
from horiba_sdk.devices.abstract_device_discovery import AbstractDeviceDiscovery
from horiba_sdk.devices.single_devices import SpectrAcq3
from horiba_sdk.icl_error import AbstractErrorDB


@final
class SpectrAcq3Discovery(AbstractDeviceDiscovery):
    def __init__(self, communicator: AbstractCommunicator, error_db: AbstractErrorDB):
        self._communicator: AbstractCommunicator = communicator
        self._spectracq3_devices: list[SpectrAcq3] = []
        self._error_db: AbstractErrorDB = error_db

    @override
    async def execute(self, error_on_no_device: bool = False) -> None:
        """
        Discovers the connected SpectrAcq3 devices and saves them internally.

        Raises:
            Exception: When no SpectrAcq3 devices are discovered and that `error_on_no_device` is set.
            Or when there is an issue parsing the SpectrAcq3 devices list
        """
        if not self._communicator.opened():
            await self._communicator.open()

        response: Response = await self._communicator.request_with_response(Command('saq3_discover', {}))
        if response.results.get('count', 0) == 0 and error_on_no_device:
            raise Exception('No SpectrAcq3 devices connected')

        response = await self._communicator.request_with_response(Command('saq3_list', {}))

        raw_device_list = response.results
        self._spectracq3_devices = self._parse_devices(raw_device_list)
        logger.info(f'Found {len(self._spectracq3_devices)} SpectrAcq3 devices')

    def _parse_devices(self, raw_device_list: dict[str, Any]) -> list[SpectrAcq3]:
        detected_devices: list[SpectrAcq3] = []
        for device in raw_device_list['devices']:
            try:
                logger.debug(f'Parsing SpectrAcq3: {device}')
                spectracq3 = SpectrAcq3(device['index'], self._communicator, self._error_db)
                logger.info(f'Detected SpectrAcq3: {device["deviceType"]}')
                detected_devices.append(spectracq3)
            except Exception as e:
                logger.error(f'Error while parsing SpectrAcq3: {e}')

        return detected_devices

    def spectracq3_devices(self) -> list[SpectrAcq3]:
        return self._spectracq3_devices
