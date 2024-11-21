import asyncio
import random

from loguru import logger

from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.devices.device_manager import DeviceManager


async def main():
    acquisition_format = AcquisitionFormat.SPECTRA
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
        await ccd.set_x_axis_conversion_type(XAxisConversionType.FROM_CCD_FIRMWARE)
        await ccd.set_acquisition_format(1, acquisition_format)
        await ccd.set_exposure_time(random.randint(1, 5))
        await ccd.set_region_of_interest()  # Set default ROI, if you want a custom ROI, pass the parameters
        logger.info(await ccd.get_speed_token())
        await ccd.set_trigger_input(True, 0, 0, 1)
        if await ccd.get_acquisition_ready():
            await ccd.acquisition_start(open_shutter=True)
            await asyncio.sleep(5)  # Wait a short period for the acquisition to start
            await ccd.acquisition_abort()
            data = await ccd.get_acquisition_data()

            logger.info(f'Data when aborted while waiting for a trigger: {data}')

    finally:
        await ccd.close()

    await device_manager.stop()


if __name__ == '__main__':
    asyncio.run(main())
