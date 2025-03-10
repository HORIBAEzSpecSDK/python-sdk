import asyncio
import os

import pytest

from horiba_sdk.core.trigger_input_polarity import TriggerInputPolarity


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


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_get_firmware_version(async_device_manager_instance):
    # arrange
    expected_firmware_version = 'O1.37 Mar 15 2018 05:10:52'
    # act
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        firmware_version = await spectracq3.get_firmware_version()
        # assert
        assert firmware_version == expected_firmware_version


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_get_fpga_version(async_device_manager_instance):
    # arrange
    expected_fpga_version = '-:0.5'
    # act
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        fpga_version = await spectracq3.get_fpga_version()
        # assert
        assert fpga_version == expected_fpga_version


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_get_board_revision(async_device_manager_instance):
    # arrange
    expected_board_revision = 'B'
    # act
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        board_revision = await spectracq3.get_board_revision()
        # assert
        assert board_revision == expected_board_revision


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_set_get_hv_bias_voltage(async_device_manager_instance):
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        hv_bias_voltage_before = await spectracq3.get_hv_bias_voltage()
        # act
        await spectracq3.set_hv_bias_voltage(49)
        hv_bias_voltage = await spectracq3.get_hv_bias_voltage()
        # assert
        assert hv_bias_voltage == 49

        # act
        await spectracq3.set_hv_bias_voltage(51)
        hv_bias_voltage = await spectracq3.get_hv_bias_voltage()
        # assert
        assert hv_bias_voltage == 51

        # restore the original hv bias voltage
        await spectracq3.set_hv_bias_voltage(hv_bias_voltage_before)


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_get_max_hv_voltage_allowed(async_device_manager_instance):
    # arrange
    expected_max_hv_voltage_allowed = 900
    # act
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        max_hv_voltage = await spectracq3.get_max_hv_voltage_allowed()
        # assert
        assert max_hv_voltage == expected_max_hv_voltage_allowed


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_define_get_acq_set(async_device_manager_instance):
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        await spectracq3.set_acq_set(10, 1, 10, 0)
        acq_set = await spectracq3.get_acq_set()
        assert acq_set['scanCount'] == 10
        assert acq_set['timeStep'] == 1
        assert acq_set['integrationTime'] == 10
        assert acq_set['externalParam'] == 0


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_data_available_after_acquisition(async_device_manager_instance):
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        # arrange
        await spectracq3.set_acq_set(2, 0, 2, 0)
        # act
        await spectracq3.acq_start(1)
        await asyncio.sleep(10)
        # assert
        try:
            assert await spectracq3.is_data_available()
        finally:
            _ = await spectracq3.get_available_data()
            await spectracq3.acq_stop()


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_acquisition(async_device_manager_instance):
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        # arrange
        await spectracq3.set_acq_set(2, 0, 2, 0)
        # act
        await spectracq3.acq_start(1)
        await asyncio.sleep(10)
        # assert
        result = await spectracq3.get_available_data()
        assert isinstance(result, list)

        # stop acquisition to prevent problems with other unit tests
        await spectracq3.acq_stop()


@pytest.mark.xfail(reason='The integration in ICL version 179 does deliver the wrong is_data_available bool value ')
@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_acq_start_stop(async_device_manager_instance):
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        # arrange
        await spectracq3.set_acq_set(2, 0, 2, 0)
        # act
        await spectracq3.acq_start(1)
        await asyncio.sleep(0.1)
        # assert
        assert spectracq3.is_busy()
        await spectracq3.acq_stop()
        await asyncio.sleep(0.1)
        assert not spectracq3.is_busy()


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_acq_pause_continue(async_device_manager_instance):
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        # arrange
        await spectracq3.set_acq_set(2, 0, 2, 0)
        # act
        await spectracq3.acq_start(1)
        await asyncio.sleep(0.1)
        await spectracq3.acq_pause()
        # Assuming some mechanism to check if acquisition paused
        await spectracq3.acq_continue()
        # Assuming some mechanism to check if acquisition continued

        # stop acquisition to prevent problems with other unit tests
        await spectracq3.acq_stop()


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
@pytest.mark.parametrize('expected_polarity', [TriggerInputPolarity.ACTIVE_LOW, TriggerInputPolarity.ACTIVE_HIGH])
async def test_set_and_get_trigger_in_polarity(async_device_manager_instance, expected_polarity):
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        # arrange
        await spectracq3.set_trigger_in_polarity(expected_polarity)
        # act
        result = await spectracq3.get_trigger_in_polarity()
        # assert
        assert result == expected_polarity.value


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_get_available_data(async_device_manager_instance):
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        data = await spectracq3.get_available_data()
        assert isinstance(data, list)


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_force_trigger(async_device_manager_instance):
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        await spectracq3.force_trigger()
        # Assuming some mechanism to verify trigger was forced


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_set_get_in_trigger_mode(async_device_manager_instance):
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        await spectracq3.set_in_trigger_mode(1)
        trigger_mode = await spectracq3.get_trigger_mode()
        assert trigger_mode['inputTriggerMode'] == 1


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_get_last_error(async_device_manager_instance):
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        last_error = await spectracq3.get_last_error()
        assert isinstance(last_error, str)


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_get_error_log(async_device_manager_instance):
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        error_log = await spectracq3.get_error_log()
        assert isinstance(error_log, str)


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_spectracq3_clear_error_log(async_device_manager_instance):
    async with async_device_manager_instance.spectracq3_devices[0] as spectracq3:
        await spectracq3.clear_error_log()
        # Assuming some mechanism to verify error log was cleared
