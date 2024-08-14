# pylint: skip-file

import os
import random
import time

import pytest
from loguru import logger

from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.clean_count_mode import CleanCountMode
from horiba_sdk.core.timer_resolution import TimerResolution
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.sync.devices.single_devices.monochromator import Monochromator


# Tell pytest to run this test only if called from the scope of this module. If any other pytest scope calls this test,
# ignore it
@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_functionality(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        # act
        chip_size = ccd.get_chip_size()
        assert chip_size.width > 0 and chip_size.height > 0

        new_exposure_time = random.randint(1000, 5000)
        ccd.set_exposure_time(new_exposure_time)
        assert ccd.get_exposure_time() == new_exposure_time

        temperature = ccd.get_temperature()
        assert temperature < 0

        _ignored_speed = ccd.get_speed_token()

        ccd.set_acquisition_format(1, AcquisitionFormat.IMAGE)
        ccd.set_region_of_interest()

        if ccd.get_acquisition_ready():
            ccd.set_acquisition_start(open_shutter=True)
            time.sleep(1)  # Wait a short period for the acquisition to start

            acquisition_busy = True
            while acquisition_busy:
                acquisition_busy = ccd.get_acquisition_busy()
                time.sleep(0.3)
                logger.info('Acquisition busy')

            acquisition_data_size = ccd.get_acquisition_data_size()
            acquisition_data = ccd.get_acquisition_data()

            assert acquisition_data_size > 0
            assert acquisition_data[0]['roi'][0]['xOrigin'] == 0
            assert acquisition_data[0]['roi'][0]['yOrigin'] == 0


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_opens(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        # act
        is_open = ccd.is_open()
        # assert
        assert is_open is True


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_gain(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        gain_token_before = 0
        gain_token_after = 1

        # act
        ccd.set_gain(gain_token_before)
        gain_before = ccd.get_gain_token()

        ccd.set_gain(gain_token_after)
        gain_after = ccd.get_gain_token()

        # assert
        assert gain_before == gain_token_before
        assert gain_after == gain_token_after


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_speed(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        speed_token_before = 0
        speed_token_after = 1

        # act
        ccd.set_speed(speed_token_before)
        speed_before = ccd.get_speed_token()

        ccd.set_speed(speed_token_after)
        speed_after = ccd.get_speed_token()

        # assert
        assert speed_before == speed_token_before
        assert speed_after == speed_token_after


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_resolution(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        # act
        resolution = ccd.get_chip_size()
        config = ccd.get_configuration()

        # assert
        assert resolution.width == int(config['chipWidth'])
        assert resolution.height == int(config['chipHeight'])


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_temperature(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        # act
        temperature = ccd.get_temperature()

        # assert
        assert temperature < 0


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_fit_parameters(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        expected_fit_params_before = [1, 0, 0, 0, 0]
        expected_fit_params_after = [0, 0, 1, 0, 0]

        # act
        ccd.set_fit_parameters(expected_fit_params_before)
        actual_fit_params_before = ccd.get_fit_parameters()

        ccd.set_fit_parameters(expected_fit_params_after)
        actual_fit_params_after = ccd.get_fit_parameters()

        # assert
        assert actual_fit_params_before == expected_fit_params_before
        assert actual_fit_params_after == expected_fit_params_after


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_timer_resolution(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        expected_timer_resolution_before = TimerResolution._1_MICROSECOND
        expected_timer_resolution_after = TimerResolution._1000_MICROSECONDS

        # act
        ccd.set_timer_resolution(TimerResolution._1_MICROSECOND)
        actual_timer_resolution_before = ccd.get_timer_resolution()

        ccd.set_timer_resolution(TimerResolution._1000_MICROSECONDS)
        actual_timer_resolution_after = ccd.get_timer_resolution()

        # assert
        assert actual_timer_resolution_before == expected_timer_resolution_before
        assert actual_timer_resolution_after == expected_timer_resolution_after


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_exposure_time(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        ccd.set_timer_resolution(TimerResolution._1000_MICROSECONDS)
        expected_exposure_time_before = 100
        expected_exposure_time_after = 110

        # act
        ccd.set_exposure_time(expected_exposure_time_before)
        actual_exposure_time_before = ccd.get_exposure_time()

        ccd.set_exposure_time(expected_exposure_time_after)
        actual_exposure_time_after = ccd.get_exposure_time()

        # assert
        assert actual_exposure_time_before == expected_exposure_time_before
        assert actual_exposure_time_after == expected_exposure_time_after


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_roi(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        ccd.set_exposure_time(100)
        ccd.set_acquisition_format(1, AcquisitionFormat.IMAGE)
        # act
        ccd.set_region_of_interest(0, 0, 0, 1000, 200, 1, 200)
        if ccd.get_acquisition_ready():
            ccd.set_acquisition_start(open_shutter=True)
            time.sleep(1)  # Wait a short period for the acquisition to start

            acquisition_busy = True
            while acquisition_busy:
                acquisition_busy = ccd.get_acquisition_busy()
                time.sleep(0.3)
                logger.info('Acquisition busy')

            acquisition_data_size = ccd.get_acquisition_data_size()
            acquisition_data = ccd.get_acquisition_data()

            # assert
            assert acquisition_data_size == 1000
            assert acquisition_data[0]['roi'][0]['xOrigin'] == 0
            assert acquisition_data[0]['roi'][0]['yOrigin'] == 0
            assert acquisition_data[0]['roi'][0]['xSize'] == 1000
            assert acquisition_data[0]['roi'][0]['ySize'] == 200
            assert acquisition_data[0]['roi'][0]['xBinning'] == 1
            assert acquisition_data[0]['roi'][0]['yBinning'] == 200


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_x_axis_conversion_type(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        expected_x_axis_conversion_type_before = XAxisConversionType.NONE
        expected_x_axis_conversion_type_after = XAxisConversionType.FROM_CCD_FIRMWARE

        # act
        ccd.set_x_axis_conversion_type(expected_x_axis_conversion_type_before)
        actual_x_axis_conversion_type_before = ccd.get_x_axis_conversion_type()

        ccd.set_x_axis_conversion_type(expected_x_axis_conversion_type_after)
        actual_x_axis_conversion_type_after = ccd.get_x_axis_conversion_type()

        assert actual_x_axis_conversion_type_before == expected_x_axis_conversion_type_before
        assert actual_x_axis_conversion_type_after == expected_x_axis_conversion_type_after


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_acquisition_count(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        expected_acquisition_count_before = 1
        expected_acquisition_count_after = 2

        # act
        ccd.set_acquisition_count(expected_acquisition_count_before)
        actual_acquisition_count_before = ccd.get_acquisition_count()

        ccd.set_acquisition_count(expected_acquisition_count_after)
        actual_acquisition_count_after = ccd.get_acquisition_count()

        # assert
        assert actual_acquisition_count_before == expected_acquisition_count_before
        assert actual_acquisition_count_after == expected_acquisition_count_after


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_clean_count(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        expected_clean_count_before = 1
        expected_clean_count_after = 2

        # act
        ccd.set_clean_count(expected_clean_count_before, CleanCountMode.UNKNOWN)
        actual_clean_count_before, _ignored_mode_before = ccd.get_clean_count()

        ccd.set_clean_count(expected_clean_count_after, CleanCountMode.UNKNOWN)
        actual_clean_count_after, _ignored_mode_after = ccd.get_clean_count()

        # assert
        assert actual_clean_count_before == expected_clean_count_before
        assert actual_clean_count_after == expected_clean_count_after


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_trigger_in(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        expected_trigger_input_before = (False, -1, -1, -1)
        (
            expected_enabled_before,
            expected_address_before,
            expected_event_before,
            expected_signal_type_before,
        ) = expected_trigger_input_before

        expected_trigger_input_after = (True, 0, 0, 0)
        (
            expected_enabled_after,
            expected_address_after,
            expected_event_after,
            expected_signal_type_after,
        ) = expected_trigger_input_after

        # act
        ccd.set_trigger_input(
            expected_enabled_before, expected_address_before, expected_event_before, expected_signal_type_before
        )
        actual_trigger_input_before = ccd.get_trigger_input()

        ccd.set_trigger_input(
            expected_enabled_after, expected_address_after, expected_event_after, expected_signal_type_after
        )
        actual_trigger_input_after = ccd.get_trigger_input()

        # assert
        assert actual_trigger_input_before == expected_trigger_input_before
        assert actual_trigger_input_after == expected_trigger_input_after


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_signal_out(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        expected_signal_output_before = (False, -1, -1, -1)
        (
            expected_enabled_before,
            expected_address_before,
            expected_event_before,
            expected_signal_type_before,
        ) = expected_signal_output_before

        expected_signal_output_after = (True, 0, 0, 0)
        (
            expected_enabled_after,
            expected_address_after,
            expected_event_after,
            expected_signal_type_after,
        ) = expected_signal_output_after

        # act
        ccd.set_signal_output(
            expected_enabled_before, expected_address_before, expected_event_before, expected_signal_type_before
        )
        actual_signal_output_before = ccd.get_signal_output()

        ccd.set_signal_output(
            expected_enabled_after, expected_address_after, expected_event_after, expected_signal_type_after
        )
        actual_signal_output_after = ccd.get_signal_output()

        # assert
        assert actual_signal_output_before == expected_signal_output_before
        assert actual_signal_output_after == expected_signal_output_after


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_acquisition_abort(sync_device_manager_instance):  # noqa: ARG001
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        # act
        ccd.set_timer_resolution(TimerResolution._1000_MICROSECONDS)
        ccd.set_exposure_time(10000)

        ccd.set_acquisition_format(1, AcquisitionFormat.IMAGE)
        ccd.set_region_of_interest()

        if ccd.get_acquisition_ready():
            ccd.set_acquisition_start(open_shutter=True)
            time.sleep(0.2)  # Wait a short period for the acquisition to start

            acquisition_busy_before_abort = ccd.get_acquisition_busy()
            ccd.set_acquisition_abort()
            time.sleep(1)
            acquisition_busy_after_abort = ccd.get_acquisition_busy()

            assert acquisition_busy_before_abort
            assert not acquisition_busy_after_abort


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_restart(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        is_open_before = ccd.is_open()

        # act
        ccd.restart()
        time.sleep(0.3)
        is_open_after = ccd.is_open()

        assert is_open_before
        assert is_open_after


def wait_mono(mono: Monochromator) -> None:
    time.sleep(0.2)
    while mono.is_busy():
        time.sleep(0.2)


@pytest.mark.skipif(os.environ.get('HAS_HARDWARE') != 'true', reason='Hardware tests only run locally')
def test_ccd_range_mode_positions(sync_device_manager_instance):  # noqa: ARG001
    # arrange
    start_wavelength = 200
    end_wavelength = 500

    mono = sync_device_manager_instance.monochromators[0]
    with sync_device_manager_instance.charge_coupled_devices[0] as ccd:
        # act
        mono.open()
        wait_mono(mono)

        ccd.set_x_axis_conversion_type(XAxisConversionType.FROM_ICL_SETTINGS_INI)
        ccd.set_acquisition_format(1, AcquisitionFormat.SPECTRA)
        ccd.set_region_of_interest()

        center_wavelengths = ccd.range_mode_center_wavelengths(mono.id(), start_wavelength, end_wavelength, 10)
        assert center_wavelengths
