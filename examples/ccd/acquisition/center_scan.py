# Dependencies: matplotlib package
import asyncio
import csv

import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

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

    try:
        # mono configuration
        if not await mono.is_initialized():
            logger.info('Initializing Monochromator...')
            await mono.initialize()
        await wait_for_mono(mono)
        current_grating = await mono.get_turret_grating()
        if await mono.get_turret_grating() != current_grating:
            logger.info('Setting grating to SECOND...')
            await mono.set_turret_grating(Monochromator.Grating.SECOND)
            await wait_for_mono(mono)

        target_wavelength = 500
        await mono.move_to_target_wavelength(target_wavelength)
        logger.info(f'Moving to target wavelength {target_wavelength}...')
        await wait_for_mono(mono)
        await mono.set_slit_position(mono.Slit.A, 0)
        await mono.set_mirror_position(mono.Mirror.ENTRANCE, mono.MirrorPosition.AXIAL)
        logger.info('Setting slit position to A and mirror position to AXIAL...')
        await wait_for_mono(mono)
        mono_wavelength = await mono.get_current_wavelength()
        logger.info(f'Mono wavelength {mono_wavelength}')

        # ccd configuration

        ccd_config = await ccd.get_configuration()
        chip_x = int(ccd_config['chipWidth'])
        chip_y = int(ccd_config['chipHeight'])
        await ccd.set_acquisition_count(1)
        await ccd.set_center_wavelength(mono.id(), mono_wavelength)
        await ccd.set_exposure_time(1000)
        await ccd.set_gain(0)  # High Light
        await ccd.set_speed(2)  # 1 MHz Ultra
        await ccd.set_timer_resolution(TimerResolution.MILLISECONDS)
        await ccd.set_acquisition_format(1, AcquisitionFormat.SPECTRA)
        await ccd.set_region_of_interest(
            1, 0, 0, chip_x, chip_y, 1, chip_y
        )  # Set default ROI, if you want a custom ROI, pass the parameters
        await ccd.set_x_axis_conversion_type(XAxisConversionType.FROM_ICL_SETTINGS_INI)

        if await ccd.get_acquisition_ready():
            logger.info('Starting acquisition...')
            await ccd.acquisition_start(open_shutter=True)
            await asyncio.sleep(1)  # Wait a short period for the acquisition to start
            await wait_for_ccd(ccd)

            raw_data = await ccd.get_acquisition_data()
            logger.info(f'Acquired data: {raw_data}')
            x_data = raw_data['acquisition'][0]['roi'][0]['xData']
            y_data = raw_data['acquisition'][0]['roi'][0]['yData']
            # for AcquisitionFormat.IMAGE:
            # xy_data = [raw_dataraw_data['acquisition'][0]['roi'][0]['yData'][0]['roi'][0]['xData'][0],
            # raw_dataraw_data['acquisition'][0]['roi'][0]['yData'][0]['roi'][0]['yData'][0]]
            with open('outputcsv.csv', 'w', newline = "") as csvfile:
                w = csv.writer(csvfile)
                fields = ['wavelength', 'intensity']
                w.writerow(fields)
                w.writerows(zip(x_data, y_data[0]))
        else:
            raise Exception('CCD not ready for acquisition')
    finally:
        await ccd.close()
        logger.info('Waiting before closing Monochromator...')
        await asyncio.sleep(1)
        logger.info('Closing Monochromator...')
        await mono.close()
        logger.info('Stopping device manager...')
        await device_manager.stop()

    await plot_values(target_wavelength, x_data, y_data)


async def plot_values(target_wavelength, x_data, y_data):
    # Plotting the data
    if len(y_data) == 1:
        plt.plot(x_data, y_data[0], linestyle='-')
        plt.title(f'Wavelength ({target_wavelength}[nm]) vs. Intensity')
        plt.xlabel('Wavelength')
        plt.ylabel('Intensity')
        plt.grid(True)
        plt.show()
    else:
        arr = np.array(y_data)
        plt.imshow(arr, interpolation='nearest', aspect='auto')
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
