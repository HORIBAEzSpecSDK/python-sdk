import asyncio
import random

from loguru import logger

from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.devices.device_manager import DeviceManager


async def subtract_dark_count(shutter_open_data: list[float], shutter_closed_data: list[float]) -> list[float]:
    values_noise_free = []
    zipped_data = zip(shutter_open_data, shutter_closed_data)
    for data in zipped_data:
        value_noise_free = data[0] - data[1]
        values_noise_free.append(value_noise_free)
    return values_noise_free


async def main():
    acquisition_format = AcquisitionFormat.IMAGE
    device_manager = DeviceManager(start_icl=True)
    await device_manager.start()

    if not device_manager.charge_coupled_devices:
        logger.error('No CCDs found, exiting...')
        await device_manager.stop()
        return

    ccd = device_manager.charge_coupled_devices[0]
    await ccd.open()

    try:
        await ccd.set_acquisition_count(1)
        await ccd.set_x_axis_conversion_type(XAxisConversionType.NONE)
        await ccd.set_acquisition_format(1, acquisition_format)
        logger.info(await ccd.get_acquisition_count())
        logger.info(await ccd.get_clean_count())
        logger.info(await ccd.get_timer_resolution())
        logger.info(await ccd.get_gain_token())
        logger.info(await ccd.get_chip_size())
        logger.info(await ccd.get_exposure_time())
        await ccd.set_exposure_time(random.randint(1, 5))
        logger.info(await ccd.get_exposure_time())
        logger.info(await ccd.get_chip_temperature())
        await ccd.set_region_of_interest()  # Set default ROI, if you want a custom ROI, pass the parameters
        logger.info(await ccd.get_speed_token())
        data_shutter_closed = []
        await ccd.set_center_wavelength()
        if await ccd.get_acquisition_ready():
            await ccd.acquisition_start(open_shutter=False)
            await asyncio.sleep(1)  # Wait a short period for the acquisition to start
            # Poll for acquisition status
            acquisition_busy = True
            while acquisition_busy:
                acquisition_busy = await ccd.get_acquisition_busy()
                await asyncio.sleep(0.3)
                logger.info('Acquisition busy')

            data_shutter_closed = await ccd.get_acquisition_data()
            logger.info(f'Data with closed shutter: {data_shutter_closed}')

        data_shutter_open = []
        if await ccd.get_acquisition_ready():
            await ccd.acquisition_start(open_shutter=True)
            await asyncio.sleep(1)  # Wait a short period for the acquisition to start
            # Poll for acquisition status
            acquisition_busy = True
            while acquisition_busy:
                acquisition_busy = await ccd.get_acquisition_busy()
                await asyncio.sleep(0.3)
                logger.info('Acquisition busy')

            data_shutter_open = await ccd.get_acquisition_data()
            logger.info(f'Data with open shutter: {data_shutter_open}')

        data_shutter_open_selected = data_shutter_open["acquisition"][0]['roi'][0]['yData'][0]
        data_shutter_closed_selected = data_shutter_closed["acquisition"][0]['roi'][0]['yData'][0]
        data_without_noise = await subtract_dark_count(data_shutter_open_selected, data_shutter_closed_selected)
        data_subtracted = data_shutter_open
        data_subtracted["acquisition"][0]['roi'][0]['yData'][0] = data_without_noise

        logger.info(f'Data without noise: {data_subtracted}')

    finally:
        await ccd.close()

    await device_manager.stop()


if __name__ == '__main__':
    asyncio.run(main())
