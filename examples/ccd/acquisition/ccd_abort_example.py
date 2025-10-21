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

    ccd_config = await ccd.get_configuration()
    chip_x = int(ccd_config['chipWidth'])
    chip_y = int(ccd_config['chipHeight'])
    
    exposure_time = 1000

    try:
        logger.info('Setting up acquisition...')
        await ccd.set_acquisition_format(1, acquisition_format)
        await ccd.set_region_of_interest(
            1, 0, 0, chip_x, chip_y, 1, chip_y
            )
        
        await ccd.set_x_axis_conversion_type(XAxisConversionType.NONE)

        await ccd.set_acquisition_count(1)
        await ccd.set_exposure_time(exposure_time)
        await ccd.set_trigger_input(True, 0, 0, 1)
        logger.info('Setting up acquisition complete')
        if await ccd.get_acquisition_ready():
            logger.info('Starting acquisition...')
            await ccd.acquisition_start(open_shutter=True)
            while True:
                try:
                    await asyncio.sleep((exposure_time/1000)*2)
                    logger.info("Trying for data...")
                    my_ccd_data = await ccd.get_acquisition_data()
                    break
                except:
                    logger.info("Data not acquired, aborting acquisition...")
                    
                    # CCD will be busy infinitely because it is waiting for a trigger that is not coming.
                    # That's why the abort command needs to be sent.
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
        # reset trigger mode
        await ccd.set_trigger_input(False, 0, 0, 1)
        await ccd.close()
        logger.info('Stopping device manager...')
        await device_manager.stop()


if __name__ == '__main__':
    asyncio.run(main())
