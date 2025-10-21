# Dependencies: matplotlib package

"""
Takes a single image acquisition and displays as an image of a 2D array.
"""

import asyncio

import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.timer_resolution import TimerResolution
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.devices.device_manager import DeviceManager


async def main():
    device_manager = DeviceManager(start_icl=True)
    await device_manager.start()

    if not device_manager.charge_coupled_devices:  # or not device_manager.monochromators:
        logger.error('Required ccd not found')
        await device_manager.stop()
        return
    
    # comment in mentions of mono if using an iHR or microHR
    #mono = device_manager.monochromators[0]
    #await mono.open()
    #await wait_for_mono(mono)
    ccd = device_manager.charge_coupled_devices[0]
    await ccd.open()

    try:
        # mono init
        #await mono.home()
        #await wait_for_mono(mono)

        # ccd configuration

        ccd_config = await ccd.get_configuration()
        chip_x = int(ccd_config['chipWidth'])
        chip_y = int(ccd_config['chipHeight'])

        # core config functions
        await ccd.set_acquisition_format(1, AcquisitionFormat.SPECTRA_IMAGE)
        await ccd.set_region_of_interest(
            1, 0, 0, chip_x, chip_y, 1, 1
        )  # Set default ROI, if you want a custom ROI, pass the parameters

        # will acquire in pixel domain
        await ccd.set_x_axis_conversion_type(XAxisConversionType.NONE)

        await ccd.set_acquisition_count(1)

        exposure_time = 1000 # in ms
        await ccd.set_timer_resolution(TimerResolution.MILLISECONDS)
        await ccd.set_exposure_time(exposure_time)

        if await ccd.get_acquisition_ready():
                logger.info('Starting acquisition...')
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

                logger.info(f'Acquired data: {raw_data}')

                # for spectra
                # xy_data = raw_data[0]['roi'][0]['xyData']

                # for image
                xy_data = [raw_data['acquisition'][0]['roi'][0]['xData'][0], 
                           raw_data['acquisition'][0]['roi'][0]['yData']]


    finally:
        await ccd.close()
        logger.info('Waiting before closing CCD')

    await plot_image(xy_data)
    await device_manager.stop()


async def plot_image(xy_data):
    arr = np.array(xy_data[1])
    plt.imshow(arr, interpolation='nearest', aspect='auto')
    plt.show()



async def wait_for_mono(mono):
    mono_busy = True
    while mono_busy:
        mono_busy = await mono.is_busy()
        await asyncio.sleep(1)
        logger.info('Mono busy...')


if __name__ == '__main__':
    asyncio.run(main())
