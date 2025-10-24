# Dependencies: matplotlib package
import asyncio

import matplotlib.pyplot as plt
from loguru import logger

from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.stitching import LinearSpectraStitch
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

    start_wavelength = 400
    end_wavelength = 600
    spectrum = [[0], [0]]

    try:
        # mono configuration
        if not await mono.is_initialized():
            await mono.initialize()
            await wait_for_mono(mono)
        await mono.set_turret_grating(Monochromator.Grating.SECOND)
        await wait_for_mono(mono)
        await mono.set_mirror_position(Monochromator.Mirror.ENTRANCE, Monochromator.MirrorPosition.AXIAL)
        await wait_for_mono(mono)
        await mono.set_slit_position(Monochromator.Slit.A, 0.5)
        await wait_for_mono(mono)
        mono_wavelength = await mono.get_current_wavelength()

        # ccd configuration

        ccd_config = await ccd.get_configuration()
        chip_x = int(ccd_config['chipWidth'])
        chip_y = int(ccd_config['chipHeight'])

        # core config functions
        await ccd.set_acquisition_format(1, AcquisitionFormat.SPECTRA_IMAGE)
        await ccd.set_region_of_interest(
            1, 0, 0, chip_x, chip_y, 1, chip_y
        )  # Set default ROI, if you want a custom ROI, pass the parameters
        await ccd.set_center_wavelength(mono.id(), mono_wavelength)
        await ccd.set_x_axis_conversion_type(XAxisConversionType.FROM_ICL_SETTINGS_INI)

        await ccd.set_acquisition_count(1)

        exposure_time = 1000 # in ms
        await ccd.set_timer_resolution(TimerResolution.MILLISECONDS)
        await ccd.set_exposure_time(exposure_time)
        await ccd.set_gain(0)  # Least sensitive
        await ccd.set_speed(0)  # Slowest, but least read noise

        center_wavelengths = await ccd.range_mode_center_wavelengths(mono.id(), start_wavelength, end_wavelength, 100)
        logger.info(f'Number of captures: {len(center_wavelengths)}')

        with open('centerwavelengths.txt', 'w') as f:
            f.write(str(center_wavelengths))
            f.close()
        
        logger.info("List of center wavelengths written to centerwavelengths.txt")

        captures = []
        for center_wavelength in center_wavelengths:
            await mono.move_to_target_wavelength(center_wavelength)
            await wait_for_mono(mono)
            mono_wavelength = await mono.get_current_wavelength()
            logger.info(f'Mono wavelength {mono_wavelength}')

            await ccd.set_center_wavelength(mono.id(), mono_wavelength)
            await wait_for_ccd(ccd)

            xy_data = await capture(ccd)
            # Add debug logging to check the data structure
            logger.debug(f'Capture data structure: {xy_data}')
            captures.append(xy_data)

        # Add debug logging before stitching
        logger.debug(f'All captures before stitching: {captures}')
        stitch = LinearSpectraStitch(captures)
        spectrum = stitch.stitched_spectra()
        # pb
        filtered_spectrum = await filter_values(start_wavelength, end_wavelength, spectrum[0], spectrum[1][0])
        with open('plot_values.txt', 'w') as t:
            t.write(str(spectrum))
            t.close()

    finally:
        await ccd.close()
        logger.info('Waiting before closing Monochromator')
        await asyncio.sleep(1)
        await mono.close()

    await device_manager.stop()

    # await plot_values(start_wavelength, end_wavelength, spectrum)
    # pb
    await plot_values(start_wavelength, end_wavelength, filtered_spectrum)


async def capture(ccd):
    xy_data = [[0], [0]]
    if await ccd.get_acquisition_ready():
        logger.info('Starting acquisition...')
        exposure_time = await ccd.get_exposure_time()
        await ccd.acquisition_start(open_shutter=True)
        raw_data = []
        while True:
            try:
                await asyncio.sleep((exposure_time/1000)*2)
                raw_data = await ccd.get_acquisition_data()
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                logger.info("Data not ready yet...")
        xy_data = [raw_data['acquisition'][0]['roi'][0]['xData'], raw_data['acquisition'][0]['roi'][0]['yData']]

    else:
        raise Exception('CCD not ready for acquisition')
    return xy_data


async def filter_values(start_wavelength, end_wavelength, wavelength_values, intensity_values):
    filtered_wavelengths = []
    filtered_intensities = []
    for wl, inten in zip(wavelength_values, intensity_values):
        if start_wavelength <= wl <= end_wavelength:
            filtered_wavelengths.append(wl)
            filtered_intensities.append(inten)
    filtered_xy = [filtered_wavelengths, filtered_intensities]
    return filtered_xy


async def plot_values(start_wavelength, end_wavelength, xy_data):
    # x_values = [data[0] for data in xy_data]
    # pb
    x_values = xy_data[0]
    # y_values = [data[1] for data in xy_data]
    # pb
    y_values = xy_data[1]

    # for image format
    # x_values = xy_data[0]
    # y_values = xy_data[1]
    # Plotting the data
    plt.plot(x_values, y_values, linestyle='-')
    plt.title(f'Range Scan {start_wavelength}-{end_wavelength}[nm] vs. Intensity')
    plt.xlabel('Wavelength')
    plt.ylabel('Intensity')
    plt.grid(True)
    plt.show()

async def wait_for_mono(mono):
    mono_busy = True
    while mono_busy:
        mono_busy = await mono.is_busy()
        await asyncio.sleep(1)
        logger.info('Mono busy...')


if __name__ == '__main__':
    asyncio.run(main())
