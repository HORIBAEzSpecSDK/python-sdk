import asyncio
import random

from loguru import logger

from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.devices.device_manager import DeviceManager


async def main():
    excitation_wavelength = 520.0
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

            data_wavelength = await ccd.get_acquisition_data()
            logger.info(f'Data with wavelength: {data_wavelength}')

            wavelengths = data_wavelength["acquisition"][0]['roi'][0]['xData']
            raman_shift = await ccd.raman_convert(wavelengths, excitation_wavelength)
            data_raman_shift = data_wavelength
            data_raman_shift["acquisition"][0]['roi'][0]['xData'][0] = raman_shift

            logger.info(f'Data without raman shift: {data_raman_shift}')

    finally:
        await ccd.close()

    await device_manager.stop()


if __name__ == '__main__':
    asyncio.run(main())
