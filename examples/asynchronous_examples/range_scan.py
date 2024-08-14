# Dependencies: matplotlib package
import asyncio

import matplotlib.pyplot as plt
from loguru import logger

from examples.asynchronous_examples.linear_spectra_stitch import LinearSpectraStitch
from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.timer_resolution import TimerResolution
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.devices.device_manager import DeviceManager
from horiba_sdk.devices.single_devices.monochromator import Monochromator


async def main():
    device_manager = DeviceManager(start_icl=True)
    await device_manager.start()

    if not device_manager.charge_coupled_devices or not device_manager.monochromators:
        logger.error('Required monochromator or ccd not found')
        await device_manager.stop()
        return

    mono = device_manager.monochromators[0]
    await mono.open()
    await wait_for_mono(mono)
    ccd = device_manager.charge_coupled_devices[0]
    await ccd.open()
    await wait_for_ccd(ccd)

    start_wavelength = 200
    end_wavelength = 600
    spectrum = [[0], [0]]

    try:
        # mono configuration
        await mono.home()
        await wait_for_mono(mono)
        await mono.set_turret_grating(Monochromator.Grating.THIRD)
        await wait_for_mono(mono)

        # ccd configuration
        await ccd.set_timer_resolution(TimerResolution._1000_MICROSECONDS)
        await ccd.set_exposure_time(50)
        await ccd.set_gain(0)  # High Light
        await ccd.set_speed(2)  # 1 MHz Ultra

        await ccd.set_x_axis_conversion_type(XAxisConversionType.FROM_ICL_SETTINGS_INI)
        await ccd.set_acquisition_format(1, AcquisitionFormat.IMAGE)
        await ccd.set_region_of_interest()  # Set default ROI, if you want a custom ROI, pass the parameters

        center_wavelengths = await ccd.range_mode_center_wavelengths(mono.id(), start_wavelength, end_wavelength, 10)
        logger.info(f'Number of captures: {len(center_wavelengths)}')

        captures = []
        for center_wavelength in center_wavelengths:
            await mono.move_to_target_wavelength(center_wavelength)
            await wait_for_mono(mono)
            mono_wavelength = await mono.get_current_wavelength()
            logger.info(f'Mono wavelength {mono_wavelength}')

            await ccd.set_center_wavelength(mono_wavelength)

            xy_data = await capture(ccd)
            captures.append(xy_data)

        stitch = LinearSpectraStitch(
            captures
        )  # You can implement your own stitching by subclassing the SpectraStitch interface
        spectrum = stitch.stitched_spectra()

    finally:
        await ccd.close()
        logger.info('Waiting before closing Monochromator')
        await asyncio.sleep(15)
        await mono.close()

    await device_manager.stop()

    await plot_values(start_wavelength, end_wavelength, spectrum)


async def capture(ccd):
    xy_data = [[0], [0]]
    if await ccd.get_acquisition_ready():
        await ccd.set_acquisition_start(open_shutter=True)
        await asyncio.sleep(1)  # Wait a short period for the acquisition to start
        await wait_for_ccd(ccd)

        raw_data = await ccd.get_acquisition_data()
        print(raw_data)
        # for AcquisitionFormat.SPECTRA:
        # xy_data = raw_data[0]['roi'][0]['xyData']
        # for AcquisitionFormat.IMAGE:
        xy_data = [raw_data[0]['roi'][0]['xData'][0], raw_data[0]['roi'][0]['yData'][0]]
        logger.info(xy_data)
    else:
        raise Exception('CCD not ready for acquisition')
    return xy_data


async def plot_values(start_wavelength, end_wavelength, xy_data):
    x_values = [data[0] for data in xy_data]
    y_values = [data[1] for data in xy_data]
    # for AcquisitionFormat.IMAGE:
    # x_values = xy_data[0]
    # y_values = xy_data[1]
    # Plotting the data
    plt.plot(x_values, y_values, linestyle='-')
    plt.title(f'Range Scan {start_wavelength}-{end_wavelength}[nm] vs. Intensity')
    plt.xlabel('Wavelength')
    plt.ylabel('Intensity')
    plt.grid(True)
    plt.show()


async def wait_for_ccd(ccd):
    acquisition_busy = True
    while acquisition_busy:
        acquisition_busy = await ccd.get_acquisition_busy()
        await asyncio.sleep(1)
        logger.info('Acquisition busy')


async def wait_for_mono(mono):
    mono_busy = True
    while mono_busy:
        mono_busy = await mono.is_busy()
        await asyncio.sleep(1)
        logger.info('Mono busy...')


if __name__ == '__main__':
    asyncio.run(main())
