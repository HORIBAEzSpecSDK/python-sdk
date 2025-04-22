import asyncio
import random

from loguru import logger

from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.devices.device_manager import DeviceManager
from horiba_sdk.devices.single_devices import Monochromator


async def main():
    excitation_wavelength = 520.0
    acquisition_format = AcquisitionFormat.SPECTRA
    device_manager = DeviceManager(start_icl=True)
    await device_manager.start()

    if not device_manager.charge_coupled_devices or not device_manager.monochromators:
        logger.error('Required monochromator or ccd not found')
        await device_manager.stop()
        return

    mono = device_manager.monochromators[0]
    await mono.open()
    await wait_for_mono(mono)

    ccd = device_manager.charge_coupled_devices[0]
    await ccd.open()
    await wait_for_ccd(ccd)

    try:
        if not await mono.is_initialized():
            logger.info('Initializing Monochromator...')
            await mono.initialize()
        await wait_for_mono(mono)
        current_grating = await mono.get_turret_grating()
        if await mono.get_turret_grating() != current_grating:
            logger.info('Setting grating to SECOND...')
            await mono.set_turret_grating(Monochromator.Grating.SECOND)
            await wait_for_mono(mono)

        target_wavelength = 500
        await mono.move_to_target_wavelength(target_wavelength)
        logger.info(f'Moving to target wavelength {target_wavelength}...')
        await wait_for_mono(mono)
        await mono.set_slit_position(mono.Slit.A, 0)
        await mono.set_mirror_position(mono.Mirror.ENTRANCE, mono.MirrorPosition.AXIAL)
        logger.info('Setting slit position to A and mirror position to AXIAL...')
        await wait_for_mono(mono)
        mono_wavelength = await mono.get_current_wavelength()
        logger.info(f'Mono wavelength {mono_wavelength}')

        await ccd.set_acquisition_count(1)
        await ccd.set_center_wavelength(mono.id(), mono_wavelength)
        await ccd.set_x_axis_conversion_type(XAxisConversionType.FROM_ICL_SETTINGS_INI)
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

            logger.info(f'Data with raman shift: {data_raman_shift}')

    finally:
        await ccd.close()

    await device_manager.stop()


async def wait_for_ccd(ccd):
    acquisition_busy = True
    while acquisition_busy:
        acquisition_busy = await ccd.get_acquisition_busy()
        await asyncio.sleep(1)
        logger.info('Acquisition busy')


async def wait_for_mono(mono):
    mono_busy = True
    while mono_busy:
        mono_busy = await mono.is_busy()
        await asyncio.sleep(1)
        logger.info('Mono busy...')


if __name__ == '__main__':
    asyncio.run(main())
