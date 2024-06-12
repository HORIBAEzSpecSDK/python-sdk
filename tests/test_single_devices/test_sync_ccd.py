# pylint: skip-file
# Important note: the fake_icl_exe will return the contents of the
# horiba_sdk/devices/fake_responses/ccd.json
# Look at /test/conftest.py for the definition of fake_icl_exe

from horiba_sdk.core.clean_count_mode import CleanCountMode
from horiba_sdk.core.timer_resolution import TimerResolution
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType


def test_ccd_opens(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        assert ccd.is_open() is True


def test_ccd_temperature(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        temperature = ccd.get_temperature()
        assert temperature < 0.0


def test_ccd_resolution(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        resolution = ccd.get_chip_size()
        assert resolution.width > 0 and resolution.height > 0


def test_ccd_speed(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        speed = ccd.get_speed_token()

        # assert
        assert speed == 0


def test_ccd_gain(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        gain = ccd.get_gain_token()

        # assert
        assert gain == 0


def test_ccd_fit_params(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        fit_params = ccd.get_fit_parameters()

        # assert
        assert fit_params == [0, 1, 0, 0, 0]


def test_ccd_timer_resolution(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        timer_resolution = ccd.get_timer_resolution()

        # assert
        assert timer_resolution == TimerResolution._1000_MICROSECONDS


def test_ccd_x_axis_conversion_type(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        x_axis_conversion_type = ccd.get_x_axis_conversion_type()

        # assert
        assert x_axis_conversion_type == XAxisConversionType.NONE


def test_ccd_acquisition_count(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        acquisition_count = ccd.get_acquisition_count()

        # assert
        assert acquisition_count == 1


def test_ccd_clean_count(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        (clean_count, clean_count_mode) = ccd.get_clean_count()

        # assert
        assert clean_count == 1
        assert clean_count_mode == CleanCountMode.Mode1


def test_ccd_acquisition_data(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        data_size = ccd.get_acquisition_data_size()

        # assert
        assert data_size == 1024


def test_ccd_exposure_time(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        exposure_time = ccd.get_exposure_time()

        # assert
        assert exposure_time == 0


def test_ccd_trigger_input(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        (enabled, address, event, signal) = ccd.get_trigger_input()

        # assert
        assert not enabled
        assert address == -1
        assert event == -1
        assert signal == -1


def test_ccd_signal_output(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        (enabled, address, event, signal_type) = ccd.get_signal_output()

        # assert
        assert enabled
        assert address == 0
        assert event == 0
        assert signal_type == 0


def test_ccd_acquisition_ready(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        acquisition_ready = ccd.get_acquisition_ready()

        # assert
        assert acquisition_ready


def test_ccd_acquisition_busy(fake_sync_icl_exe, fake_sync_device_manager):  # noqa: ARG001
    # arrange
    # act
    with fake_sync_device_manager.charge_coupled_devices[0] as ccd:
        # assert
        acquisition_busy = ccd.get_acquisition_busy()

        # assert
        assert not acquisition_busy
