import asyncio
import random

from loguru import logger

from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.devices.device_manager import DeviceManager


async def main():
    acquisition_format = AcquisitionFormat.SPECTRA_IMAGE
    device_manager = DeviceManager(start_icl=True)
    await device_manager.start()

    if not device_manager.charge_coupled_devices:
        logger.error('No CCDs found, exiting...')
        await device_manager.stop()
        return

    ccd = device_manager.charge_coupled_devices[0]
    await ccd.open()

    try:
        logger.info('Setting up acquisition...')
        await ccd.set_acquisition_count(1)
        await ccd.set_x_axis_conversion_type(XAxisConversionType.FROM_CCD_FIRMWARE)
        await ccd.set_acquisition_format(1, acquisition_format)
        await ccd.set_exposure_time(random.randint(1, 5))
        await ccd.set_region_of_interest()  # Set default ROI, if you want a custom ROI, pass the parameters
        await ccd.set_trigger_input(True, 0, 0, 1)
        logger.info('Setting up acquisition complete')
        if await ccd.get_acquisition_ready():
            logger.info('Starting acquisition...')
            await ccd.acquisition_start(open_shutter=True)
            while await ccd.get_acquisition_busy():
                # CCD will be busy infinitely because it is waiting for a trigger that is not coming.
                # That's why the abort command needs to be sent.
                await asyncio.sleep(0.3)
                logger.info('Aborting acquisition...')
                await ccd.acquisition_abort()
            data = await ccd.get_acquisition_data()
            logger.info(f'Data when aborted while waiting for a trigger: {data}')

    except Exception as e:
        logger.error(f'Error: {e}')

    finally:
        logger.info('Restarting CCD...')
        # restart the CCD to reset the trigger
        await ccd.restart()
        await asyncio.sleep(7)
        await ccd.close()
        logger.info('Stopping device manager...')
        await device_manager.stop()


if __name__ == '__main__':
    asyncio.run(main())
