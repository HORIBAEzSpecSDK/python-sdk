# pylint: skip-file
import asyncio
import os

import pytest

from horiba_sdk.devices.single_devices import Monochromator


@pytest.fixture(scope='session')
def event_loop(request):  # noqa: ARG001
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_monochromator_opens(async_device_manager_instance):
    # arrange
    # act
    async with async_device_manager_instance.monochromators[0] as monochromator:
        # assert
        assert await monochromator.is_open() is True


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_monochromator_busy(async_device_manager_instance):
    # arrange
    async with async_device_manager_instance.monochromators[0] as monochromator:
        # act
        # assert
        assert await monochromator.is_busy() is False


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_monochromator_init(async_device_manager_instance):
    # arrange
    async with async_device_manager_instance.monochromators[0] as monochromator:
        # act
        await monochromator.home()

        while await monochromator.is_busy():
            await asyncio.sleep(1)

        # assert
        assert await monochromator.is_busy() is False


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_monochromator_config(async_device_manager_instance):  # noqa: ARG001
    # arrange
    async with async_device_manager_instance.monochromators[0] as monochromator:
        # act
        config = await monochromator.configuration()

        # assert
        assert config
        assert config != ''


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_monochromator_wavelength(async_device_manager_instance):
    # arrange
    async with async_device_manager_instance.monochromators[0] as monochromator:
        # act
        await monochromator.move_to_target_wavelength(100)

        while await monochromator.is_busy():
            await asyncio.sleep(1)

        # assert
        assert await monochromator.get_current_wavelength() > 0


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_monochromator_calibrate_wavelength(async_device_manager_instance):
    # arrange
    async with async_device_manager_instance.monochromators[0] as monochromator:
        # act
        # TODO: How to test this properly???
        # await monochromator.calibrate_wavelength(350)

        # assert
        # assert await monochromator.get_current_wavelength() > 0
        assert not await monochromator.is_busy()


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
@pytest.mark.asyncio
async def test_monochromator_turret_grating_position(async_device_manager_instance):
    # arrange
    async with async_device_manager_instance.monochromators[0] as monochromator:
        expected_grating = Monochromator.Grating.FIRST

        # act
        await monochromator.set_turret_grating(expected_grating)

        while await monochromator.is_busy():
            await asyncio.sleep(1)

        actual_grating = await monochromator.get_turret_grating()

        # assert
        assert actual_grating == expected_grating


# Note: Filter wheel not available on our mono
@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_monochromator_filter_wheel(async_device_manager_instance):  # noqa: ARG001
    # arrange
    async with async_device_manager_instance.monochromators[0] as monochromator:
        filter_wheel = Monochromator.FilterWheel.SECOND
        expected_filter_wheel_position_before = Monochromator.FilterWheelPosition.RED
        expected_filter_wheel_position_after = Monochromator.FilterWheelPosition.GREEN

        # act
        await monochromator.set_filter_wheel_position(filter_wheel, expected_filter_wheel_position_before)
        await asyncio.sleep(0.4)
        while await monochromator.is_busy():
            await asyncio.sleep(1)
        actual_filter_wheel_position_before = await monochromator.get_filter_wheel_position(filter_wheel)

        await monochromator.set_filter_wheel_position(filter_wheel, expected_filter_wheel_position_after)
        await asyncio.sleep(0.4)
        while await monochromator.is_busy():
            await asyncio.sleep(1)
        actual_filter_wheel_position_after = await monochromator.get_filter_wheel_position(filter_wheel)

        # assert
        assert actual_filter_wheel_position_before == expected_filter_wheel_position_before
        assert actual_filter_wheel_position_after == expected_filter_wheel_position_after


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_monochromator_mirror(async_device_manager_instance):  # noqa: ARG001
    # arrange
    async with async_device_manager_instance.monochromators[0] as monochromator:
        expected_mirror_position_before = Monochromator.MirrorPosition.LATERAL
        expected_mirror_position_after = Monochromator.MirrorPosition.AXIAL
        timeout_s = 120
        await monochromator.home()
        current_time = 0
        await asyncio.sleep(0.4)
        while await monochromator.is_busy() and current_time < timeout_s:
            await asyncio.sleep(1)
            current_time += 1
            if current_time >= timeout_s:
                raise TimeoutError('Timeout error')
        # act
        await monochromator.set_mirror_position(Monochromator.Mirror.ENTRANCE, expected_mirror_position_before)
        current_time = 0
        await asyncio.sleep(0.4)
        while await monochromator.is_busy() and current_time < timeout_s:
            await asyncio.sleep(1)
            current_time += 1
            if current_time >= timeout_s:
                raise TimeoutError('Timeout error')

        actual_mirror_position_before = await monochromator.get_mirror_position(Monochromator.Mirror.ENTRANCE)

        await monochromator.set_mirror_position(Monochromator.Mirror.ENTRANCE, expected_mirror_position_after)
        current_time = 0
        while await monochromator.is_busy() and current_time < timeout_s:
            await asyncio.sleep(1)
            current_time += 1
            if current_time >= timeout_s:
                raise TimeoutError('Timeout error')

        actual_mirror_position_after = await monochromator.get_mirror_position(Monochromator.Mirror.ENTRANCE)

        # assert
        assert actual_mirror_position_before == expected_mirror_position_before
        assert actual_mirror_position_after == expected_mirror_position_after


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_monochromator_slit(async_device_manager_instance):  # noqa: ARG001
    # arrange
    async with async_device_manager_instance.monochromators[0] as monochromator:
        timeout_s = 120
        await monochromator.home()
        current_time = 0
        while await monochromator.is_busy() and current_time < timeout_s:
            await asyncio.sleep(1)
            current_time += 1
            if current_time >= timeout_s:
                raise TimeoutError('Timeout error')

        expected_slit_position_mm_before = 1.5
        expected_slit_position_mm_after = 2.6
        slit = Monochromator.Slit.A

        # act
        await monochromator.set_slit_position(slit, expected_slit_position_mm_before)
        current_time = 0
        while await monochromator.is_busy() and current_time < timeout_s:
            await asyncio.sleep(1)
            current_time += 1
            if current_time >= timeout_s:
                raise TimeoutError('Timeout error')

        actual_slit_position_mm_before = await monochromator.get_slit_position_in_mm(slit)

        await monochromator.set_slit_position(slit, expected_slit_position_mm_after)
        current_time = 0
        while await monochromator.is_busy() and current_time < timeout_s:
            await asyncio.sleep(1)
            current_time += 1
            if current_time >= timeout_s:
                raise TimeoutError('Timeout error')

        actual_slit_position_mm_after = await monochromator.get_slit_position_in_mm(slit)

        # assert
        assert (actual_slit_position_mm_before - expected_slit_position_mm_before) < 10e-9
        assert (actual_slit_position_mm_after - expected_slit_position_mm_after) < 10e-9


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_monochromator_shutter(async_device_manager_instance):
    # arrange
    async with async_device_manager_instance.monochromators[0] as monochromator:
        expected_shutter_position_before = Monochromator.ShutterPosition.CLOSED
        expected_shutter_position_after = Monochromator.ShutterPosition.OPENED

        # act
        await monochromator.close_shutter()
        actual_shutter_status_before = await monochromator.get_shutter_position(Monochromator.Shutter.FIRST)

        await monochromator.open_shutter()
        actual_shutter_status_after = await monochromator.get_shutter_position(Monochromator.Shutter.FIRST)

        # assert
        assert actual_shutter_status_before == expected_shutter_position_before
        assert actual_shutter_status_after == expected_shutter_position_after


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
async def test_monochromator_slit_step_position(async_device_manager_instance):  # noqa: ARG001
    # arrange
    async with async_device_manager_instance.monochromators[0] as monochromator:
        await monochromator.home()
        while await monochromator.is_busy():
            await asyncio.sleep(1)

        expected_slit_position_before = 200
        expected_slit_position_after = 300
        slit = Monochromator.Slit.A

        # act
        await monochromator.set_slit_step_position(slit, expected_slit_position_before)
        while await monochromator.is_busy():
            await asyncio.sleep(1)

        actual_slit_position_before = await monochromator.get_slit_step_position(slit)

        await monochromator.set_slit_step_position(slit, expected_slit_position_after)
        while await monochromator.is_busy():
            await asyncio.sleep(1)

        actual_slit_position_after = await monochromator.get_slit_step_position(slit)

        # assert
        assert actual_slit_position_before == expected_slit_position_before
        assert actual_slit_position_after == expected_slit_position_after
