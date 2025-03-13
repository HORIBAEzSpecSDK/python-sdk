# pylint: skip-file
import asyncio
import os

import pytest
import pytest_asyncio

from horiba_sdk.devices import DeviceManager as AsyncDeviceManager
from horiba_sdk.devices import FakeDeviceManager
from horiba_sdk.devices.fake_icl_server import FakeICLServer

fake_icl_host: str = 'localhost'
fake_icl_port: int = 8766
fake_icl_uri: str = 'ws://' + fake_icl_host + ':' + str(fake_icl_port)


@pytest.fixture(scope='module')
def fake_icl_host_fixture():
    return fake_icl_host


@pytest.fixture(scope='module')
def fake_icl_port_fixture():
    return fake_icl_port


@pytest.fixture(scope='module')
def fake_icl_uri_fixture():
    return fake_icl_uri


@pytest.fixture(scope='module')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='module')
async def fake_icl_exe(event_loop):  # noqa: ARG001
    server = FakeICLServer(fake_icl_host=fake_icl_host, fake_icl_port=fake_icl_port)
    await server.start()

    yield server

    await server.stop()


@pytest.fixture(scope='module')
async def fake_device_manager(event_loop):  # noqa: ARG001
    fake_device_manager = FakeDeviceManager(host=fake_icl_host, port=fake_icl_port)

    yield fake_device_manager


@pytest_asyncio.fixture(scope='module')
async def async_device_manager_instance():
    icl_ip_for_tests = os.environ.get('TEST_ICL_IP')
    icl_port_for_tests = os.environ.get('TEST_ICL_PORT')
    icl_on_remote_computer = icl_ip_for_tests is not None and icl_port_for_tests is not None
    if icl_on_remote_computer:
        device_manager = AsyncDeviceManager(start_icl=False, icl_ip=icl_ip_for_tests, icl_port=icl_port_for_tests)
    else:
        device_manager = AsyncDeviceManager(start_icl=True)

    await device_manager.start()

    yield device_manager

    await device_manager.stop()
