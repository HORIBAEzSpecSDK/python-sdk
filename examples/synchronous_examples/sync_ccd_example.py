import time

from loguru import logger

from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.timer_resolution import TimerResolution
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.sync.devices import DeviceManager


def main():
    # Start the ICL to allow communication with the devices.
    device_manager = DeviceManager(start_icl=True)
    device_manager.start()

    print(f'CCDs: {len(device_manager.charge_coupled_devices)}')
    if len(device_manager.charge_coupled_devices) == 0:
        logger.error('No CCDs discovered')
        device_manager.stop()
        return

    ccd = device_manager.charge_coupled_devices[0]
    ccd.open()

    resolution = ccd.get_chip_size()
    print(f'Resolution {resolution.width} x {resolution.height} pixels')

    ccd.set_exposure_time(5)
    print(f'Exposure time: {ccd.get_exposure_time()}')

    ccd.set_acquisition_format(1, AcquisitionFormat.SPECTRA)
    ccd.set_acquisition_count(1)
    ccd.set_x_axis_conversion_type(XAxisConversionType.NONE)
    ccd.set_timer_resolution(TimerResolution._1000_MICROSECONDS)
    ccd.set_region_of_interest()  # Set default ROI, if you want a custom ROI, pass the parameters

    ccd.acquisition_start(open_shutter=False)
    while ccd.get_acquisition_busy():
        time.sleep(1)
        logger.info('acquisition busy, sleeping 1s')

    data = ccd.get_acquisition_data()
    print(f'Acquisition data: {data}')
    time.sleep(1)
    # Close the CCD
    ccd.close()

    device_manager.stop()


if __name__ == '__main__':
    main()
