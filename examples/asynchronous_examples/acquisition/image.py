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
        logger.error('Required monochromator or ccd not found')
        await device_manager.stop()
        return

    # mono = device_manager.monochromators[0]
    # await mono.open()
    # await wait_for_mono(mono)
    ccd = device_manager.charge_coupled_devices[0]
    await ccd.open()
    await wait_for_ccd(ccd)

    try:
        # mono init
        # await mono.home()
        # await wait_for_mono(mono)

        # ccd config
        await ccd.set_x_axis_conversion_type(XAxisConversionType.NONE)
        await ccd.set_timer_resolution(TimerResolution._1000_MICROSECONDS)
        await ccd.set_exposure_time(1)
        await ccd.set_acquisition_format(1, AcquisitionFormat.IMAGE)
        await ccd.set_gain(0)  # High Light
        await ccd.set_speed(2)  # 1 MHz Ultra

        ccd_config = await ccd.get_configuration()
        chip_width = int(ccd_config['chipWidth'])
        chip_height = int(ccd_config['chipHeight'])
        await ccd.set_region_of_interest(1, 0, 0, chip_width, chip_height, 1, 1)

        if await ccd.get_acquisition_ready():
            await ccd.acquisition_start(open_shutter=True)
            await wait_for_ccd(ccd)

            raw_data = await ccd.get_acquisition_data()

        # for AcquisitionFormat.SPECTRA
        # xy_data = raw_data[0]['roi'][0]['xyData']

        # for AcquisitionFormat.IMAGE
        xy_data = [raw_data[0]['roi'][0]['xData'][0], raw_data[0]['roi'][0]['yData']]

        await plot_image(xy_data)

    finally:
        await ccd.close()
        logger.info('Waiting before closing Monochromator')

    await device_manager.stop()


async def plot_image(xy_data):
    arr = np.array(xy_data[1])
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
