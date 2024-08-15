import asyncio
import random

from loguru import logger

from horiba_sdk.devices.device_manager import DeviceManager


async def main():
    device_manager = DeviceManager()
    await device_manager.start()

    if not device_manager.charge_coupled_devices:
        logger.error('No CCDs found, exiting...')
        await device_manager.stop()
        return

    async with device_manager.charge_coupled_devices[0] as ccd:  # ChargeCoupledDevice
        chip_size = await ccd.get_chip_size()
        logger.info(f'Chip size is {chip_size}')

        await ccd.set_exposure_time(random.randint(1, 5))
        exposure_time = await ccd.get_exposure_time()
        logger.info(f'Exposure time: {exposure_time}')

        chip_temperature = await ccd.get_temperature()
        logger.info(f'Chip temperature: {chip_temperature}')

        speed = await ccd.get_speed_token()
        logger.info(f'Speed token: {speed}')

        await ccd.set_region_of_interest()  # Set default ROI, if you want a custom ROI, pass the parameters
        if await ccd.get_acquisition_ready():
            await ccd.set_acquisition_start(open_shutter=True)
            await asyncio.sleep(1)  # Wait a short period for the acquisition to start
            # Poll for acquisition status
            acquisition_busy = True
            while acquisition_busy:
                acquisition_busy = await ccd.get_acquisition_busy()
                await asyncio.sleep(1)
                logger.info('Acquisition busy')

            acquisition_data = await ccd.get_acquisition_data()
            logger.info(f'Acquisition data: {acquisition_data}')

    await asyncio.sleep(1)
    await device_manager.stop()


if __name__ == '__main__':
    asyncio.run(main())
