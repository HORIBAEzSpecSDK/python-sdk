import asyncio

from loguru import logger

from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.timer_resolution import TimerResolution
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

        # ccd configuration

        ccd_config = await ccd.get_configuration()
        chip_x = int(ccd_config['chipWidth'])
        chip_y = int(ccd_config['chipHeight'])

        # core config functions
        await ccd.set_acquisition_format(1, AcquisitionFormat.SPECTRA_IMAGE)
        await ccd.set_region_of_interest(
            1, 0, 0, chip_x, chip_y, 1, chip_y
        )  # Set default ROI, if you want a custom ROI, pass the parameters
        await ccd.set_x_axis_conversion_type(XAxisConversionType.NONE)

        await ccd.set_acquisition_count(1)

        exposure_time = 1000 # in ms
        await ccd.set_timer_resolution(TimerResolution.MILLISECONDS)
        await ccd.set_exposure_time(1000)
        await ccd.set_gain(0)  # Least sensitive
        await ccd.set_speed(0)  # Slowest, but least read noise

        await ccd.set_acquisition_count(1)

        logger.info(await ccd.get_acquisition_count())
        logger.info(await ccd.get_timer_resolution())
        logger.info(await ccd.get_exposure_time())
        logger.info(await ccd.get_gain_token())
        logger.info(await ccd.get_speed_token())
        logger.info(await ccd.get_chip_size())
        logger.info(await ccd.get_chip_temperature())
        

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

    finally:
        await ccd.close()

    await device_manager.stop()


if __name__ == '__main__':
    asyncio.run(main())
