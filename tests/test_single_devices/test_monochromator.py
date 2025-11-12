# pylint: skip-file
# Important note: the FakeDeviceManager will return the contents of the
# horiba_sdk/devices/fake_responses/monochromator.json
import pytest

from horiba_sdk.devices.single_devices import Monochromator


@pytest.mark.asyncio
async def test_monochromator_opens(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    monochromator = fake_device_manager.monochromators[0]

    # act
    await monochromator.open()

    # assert
    assert await monochromator.is_open() is True

    await monochromator.close()


@pytest.mark.asyncio
async def test_monochromator_busy(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    # act
    async with fake_device_manager.monochromators[0] as monochromator:
        # assert
        assert await monochromator.is_busy() is False


@pytest.mark.asyncio
async def test_monochromator_config(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # act
        config = await monochromator.configuration()
        # assert
        assert config
        assert config != ''


@pytest.mark.asyncio
async def test_monochromator_wavelength(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # assert
        assert await monochromator.get_current_wavelength() > 0


@pytest.mark.asyncio
async def test_monochromator_can_move_to_wavelength(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # assert
        await monochromator.move_to_target_wavelength(350)
        assert await monochromator.get_current_wavelength() > 0


@pytest.mark.asyncio
async def test_monochromator_turret_grating_position(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # act
        # assert
        assert await monochromator.get_turret_grating() == Monochromator.Grating.SECOND


@pytest.mark.asyncio
async def test_monochromator_can_select_turret_grating(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # act
        await monochromator.set_turret_grating(Monochromator.Grating.SECOND)
        # assert
        assert await monochromator.get_turret_grating() == Monochromator.Grating.SECOND


@pytest.mark.asyncio
async def test_monochromator_filter_wheel(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # act
        # assert
        assert (
            await monochromator.get_filter_wheel_position(Monochromator.FilterWheel.INTERNAL)
            == Monochromator.FilterWheelPosition.FIRST
        )


@pytest.mark.asyncio
async def test_monochromator_change_filter_wheel_position(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # act
        await monochromator.set_filter_wheel_position(
            Monochromator.FilterWheel.INTERNAL, Monochromator.FilterWheelPosition.FIRST
        )
        # assert
        assert (
            await monochromator.get_filter_wheel_position(Monochromator.FilterWheel.INTERNAL)
            == Monochromator.FilterWheelPosition.FIRST
        )


@pytest.mark.asyncio
async def test_monochromator_mirror_position(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # act
        # assert
        assert (
            await monochromator.get_mirror_position(Monochromator.Mirror.ENTRANCE) == Monochromator.MirrorPosition.AXIAL
        )


@pytest.mark.asyncio
async def test_monochromator_change_mirror_position(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # act
        await monochromator.set_mirror_position(Monochromator.Mirror.ENTRANCE, Monochromator.MirrorPosition.AXIAL)
        # assert
        assert (
            await monochromator.get_mirror_position(Monochromator.Mirror.ENTRANCE) == Monochromator.MirrorPosition.AXIAL
        )


@pytest.mark.asyncio
async def test_monochromator_get_slit_position(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # act
        # assert
        assert await monochromator.get_slit_position_in_mm(Monochromator.Slit.A) >= 0


@pytest.mark.asyncio
async def test_monochromator_set_slit_position(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # act
        await monochromator.set_slit_position(Monochromator.Slit.A, 0.0)
        # assert
        assert await monochromator.get_slit_position_in_mm(Monochromator.Slit.A) == 0


@pytest.mark.asyncio
async def test_monochromator_get_slit_step_position(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # act
        # assert
        assert await monochromator.get_slit_step_position(Monochromator.Slit.A) == 0


@pytest.mark.asyncio
async def test_monochromator_set_slit_step_position(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # act
        await monochromator.set_slit_step_position(Monochromator.Slit.A, 0)
        # assert
        assert await monochromator.get_slit_step_position(Monochromator.Slit.A) == 0


@pytest.mark.asyncio
async def test_monochromator_shutter_position(fake_device_manager, fake_icl_exe):  # noqa: ARG001
    # arrange
    async with fake_device_manager.monochromators[0] as monochromator:
        # act
        await monochromator.close_shutter()
        # assert
        assert (
            await monochromator.get_shutter_position(Monochromator.Shutter.FIRST)
            == Monochromator.ShutterPosition.CLOSED
        )
