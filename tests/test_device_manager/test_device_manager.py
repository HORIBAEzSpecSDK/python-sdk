# pylint: skip-file

import os

import psutil
import pytest

from horiba_sdk.communication import Command
from horiba_sdk.devices import DeviceManager


def is_icl_running() -> bool:
    return any(process.info['name'] == 'icl.exe' for process in psutil.process_iter(['pid', 'name']))


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.environ.get('HAS_HARDWARE') != 'true' or (os.environ.get('TEST_ICL_IP') and os.environ.get('TEST_ICL_PORT')),
    reason='Hardware tests only run locally',
)
async def test_device_manager_start_icl(event_loop):  # noqa: ARG001
    device_manager = DeviceManager(start_icl=True)
    await device_manager.start()
    assert is_icl_running(), 'ICL software is not running on the system'
    await device_manager.stop()
    assert not is_icl_running(), 'ICL software is still running on the system'


async def test_device_manager_with_fake_icl_exe(event_loop, fake_icl_exe, fake_icl_host_fixture, fake_icl_port_fixture):  # noqa: ARG001
    device_manager = DeviceManager(start_icl=False, icl_ip=fake_icl_host_fixture, icl_port=fake_icl_port_fixture)
    await device_manager.start()
    communicator = device_manager.communicator

    info_response = await communicator.request_with_response(Command('icl_info', {}))

    assert 'nodeVersion' in info_response.results
    assert communicator.opened()
    assert len(device_manager.charge_coupled_devices) == 1  # defined in horiba_sdk/devices/fake_responses/ccd.json
    assert len(device_manager.monochromators) == 1  # defined in horiba_sdk/devices/fake_responses/monochromator.json

    await device_manager.stop()
