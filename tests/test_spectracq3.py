from unittest.mock import AsyncMock

import pytest

from horiba_sdk.communication import AbstractCommunicator, Response
from horiba_sdk.devices.single_devices.spectracq3 import SpectrAcq3
from horiba_sdk.icl_error import AbstractErrorDB


@pytest.fixture
async def spectracq3_device() -> SpectrAcq3:
    """
    Fixture to create a SpectrAcq3 device instance with mocked dependencies.

    This fixture provides a SpectrAcq3 instance with mocked communicator and error database, allowing for isolated
    testing of the device's methods without requiring actual device communication.

    Returns:
        SpectrAcq3: An instance of the SpectrAcq3 device.
    """
    communicator = AsyncMock(spec=AbstractCommunicator)
    error_db = AsyncMock(spec=AbstractErrorDB)
    device = SpectrAcq3(device_id=1, communicator=communicator, error_db=error_db)
    return device


@pytest.mark.asyncio
async def test_open_device(spectracq3_device: SpectrAcq3):
    """
    Test opening the SpectrAcq3 device.

    This test verifies that the open method sends the correct command to the device, ensuring that the device
    connection is established as expected.
    """
    await spectracq3_device.open()
    spectracq3_device._communicator.send_command.assert_called_with('spectracq3_open')


@pytest.mark.asyncio
async def test_close_device(spectracq3_device: SpectrAcq3):
    """
    Test closing the SpectrAcq3 device.

    This test verifies that the close method sends the correct command to the device, ensuring that the device
    connection is terminated as expected.
    """
    await spectracq3_device.close()
    spectracq3_device._communicator.send_command.assert_called_with('spectracq3_close')


@pytest.mark.asyncio
async def test_get_serial_number(spectracq3_device: SpectrAcq3):
    """
    Test retrieving the serial number of the SpectrAcq3 device.

    This test verifies that the get_serial_number method sends the correct command and correctly processes the
    response to return the device's serial number.
    """
    expected_serial_number = "SNPG18010036"
    spectracq3_device._communicator.send_command.return_value = Response(data={'serial_number': expected_serial_number})

    serial_number = await spectracq3_device.get_serial_number()
    spectracq3_device._communicator.send_command.assert_called_with('spectracq3_getSerialNumber')
    assert serial_number == expected_serial_number 