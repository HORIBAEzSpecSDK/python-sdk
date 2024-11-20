import asyncio
import random

from loguru import logger

from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.devices.device_manager import DeviceManager


async def subtract_dark_count(
    shutter_open_data: list, shutter_closed_data: list, acquisition_format: AcquisitionFormat
) -> list:
    noise_data = []
    zipped_data = zip(shutter_open_data, shutter_closed_data)
    if acquisition_format == AcquisitionFormat.SPECTRA:
        for wavelength in zipped_data:
            noise = wavelength[0][1] - wavelength[1][1]
            noise_data.append([wavelength[0][0], noise])

    if acquisition_format == AcquisitionFormat.IMAGE:
        for pixel in zipped_data:
            noise = pixel[0] - pixel[1]
            noise_data.append(noise)
    return noise_data


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

        if acquisition_format == AcquisitionFormat.IMAGE:
            data_shutter_open_selected = data_shutter_open[0]['roi'][0]['yData'][0]
            data_shutter_closed_selected = data_shutter_closed[0]['roi'][0]['yData'][0]
            data_without_noise = await subtract_dark_count(
                data_shutter_open_selected, data_shutter_closed_selected, acquisition_format
            )
            data_shutter_open[0]['roi'][0]['yData'][0] = data_without_noise

        elif acquisition_format == AcquisitionFormat.SPECTRA:
            data_shutter_open_selected = data_shutter_open[0]['roi'][0]['xyData']
            data_shutter_closed_selected = data_shutter_closed[0]['roi'][0]['xyData']
            data_without_noise = await subtract_dark_count(
                data_shutter_open_selected, data_shutter_closed_selected, acquisition_format
            )
            data_shutter_open[0]['roi'][0]['xyData'] = data_without_noise

        logger.info(f'Data without noise: {data_shutter_open}')

    finally:
        await ccd.close()

    await device_manager.stop()


if __name__ == '__main__':
    asyncio.run(main())
