"""
This example demonstrates how to adjust the logging level.
It explains how logging is enabled and disabled for the SDK library.
This might be necessary because too much debugging
information leads to IDE behaviours that might be too sluggish.

Log levels are a widely used concept in logging. They specify the severity of a log record so that messages can be
filtered or prioritized based on how urgent they are.
Loguru offers seven unique log levels, and each one is associated with an integer value as shown in the list below:

TRACE (5): used to record fine-grained information about the program's execution path for diagnostic purposes.
DEBUG (10): used by developers to record messages for debugging purposes.
INFO (20): used to record informational messages that describe the normal operation of the program.
SUCCESS (25): similar to INFO but used to indicate the success of an operation.
WARNING (30): used to indicate an unusual event that may require further investigation.
ERROR (40): used to record error conditions that affected a specific operation.
CRITICAL (50): used to record error conditions that prevent a core function from working.
"""

import asyncio
import random
import sys

from loguru import logger

from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.devices.device_manager import DeviceManager


async def main():
    # This enables specifically logging messages from the horiba SDK library
    device_manager = DeviceManager(start_icl=True, enable_logging=True)
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
        await ccd.set_exposure_time(random.randint(1, 5))
        logger.info(await ccd.get_exposure_time())
        logger.info(await ccd.get_chip_temperature())
        await ccd.set_region_of_interest()  # Set default ROI, if you want a custom ROI, pass the parameters
        logger.info(await ccd.get_speed_token())
        if await ccd.get_acquisition_ready():
            await ccd.acquisition_start(open_shutter=True)
            await asyncio.sleep(1)  # Wait a short period for the acquisition to start
            # Poll for acquisition status
            acquisition_busy = True
            while acquisition_busy:
                acquisition_busy = await ccd.get_acquisition_busy()
                await asyncio.sleep(0.3)
                logger.info('Acquisition busy')

            logger.info(await ccd.get_acquisition_data())
    finally:
        await ccd.close()

    await device_manager.stop()


if __name__ == '__main__':
    """
    When you import the loguru module, a default logger is created. This main function removes this default logger
    and adds a new logger that has an increasing level.
    """
    logger.remove()
    # Use which logger level you need
    # logger.add(sys.stdout, level='TRACE')
    # logger.add(sys.stderr, level="DEBUG")
    logger.add(sys.stderr, level="INFO")
    asyncio.run(main())
