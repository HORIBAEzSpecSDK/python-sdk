import os

import pytest


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_open_close(async_device_manager_instance):
    # arrange
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        # act
        is_open = await spectracq3.is_open()

        # assert
        assert is_open

@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_get_serial_number(async_device_manager_instance):
    # arrange
    expected_serial_number = 'SNPG18010036'
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        # act
        serial_number = await spectracq3.get_serial_number()

        # assert
        assert serial_number == expected_serial_number
