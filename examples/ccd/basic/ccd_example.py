import asyncio
import random

from loguru import logger

from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.devices.device_manager import DeviceManager


async def main():
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
        logger.info(await ccd.get_acquisition_count())
        logger.info(await ccd.get_clean_count())
        logger.info(await ccd.get_timer_resolution())
        logger.info(await ccd.get_gain_token())
        logger.info(await ccd.get_chip_size())
        logger.info(await ccd.get_exposure_time())
        exposure_time = random.randint(1, 5)
        await ccd.set_exposure_time(exposure_time)
        logger.info(await ccd.get_exposure_time())
        logger.info(await ccd.get_chip_temperature())
        await ccd.set_region_of_interest()  # Set default ROI, if you want a custom ROI, pass the parameters
        logger.info(await ccd.get_speed_token())
        if await ccd.get_acquisition_ready():
            await ccd.acquisition_start(open_shutter=True)
            await asyncio.sleep(exposure_time)  # While the acquisition happens, we can yield the processor
            # Poll for acquisition status
            acquisition_busy = True
            while acquisition_busy:
                acquisition_busy = await ccd.get_acquisition_busy()
                await asyncio.sleep(0.1)  # Acquisition should be done, so we can poll pretty fast
                logger.info('Acquisition busy')
            my_ccd_data = await ccd.get_acquisition_data()
            logger.info(my_ccd_data)
    finally:
        await ccd.close()

    await device_manager.stop()


if __name__ == '__main__':
    asyncio.run(main())
