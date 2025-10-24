import asyncio

from loguru import logger

from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.timer_resolution import TimerResolution
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.devices.device_manager import DeviceManager
from horiba_sdk.devices.single_devices import Monochromator


async def main():
    excitation_wavelength = float(input('Enter the excitation wavelength (float value): '))
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

        target_wavelength = float(input('Enter the target wavelength (float value): '))
        await mono.move_to_target_wavelength(target_wavelength)
        logger.info(f'Moving to target wavelength {target_wavelength}...')
        await wait_for_mono(mono)
        await mono.set_slit_position(mono.Slit.A, 0)
        await mono.set_mirror_position(mono.Mirror.ENTRANCE, mono.MirrorPosition.AXIAL)
        logger.info('Setting slit position to A and mirror position to AXIAL...')
        await wait_for_mono(mono)
        mono_wavelength = await mono.get_current_wavelength()
        logger.info(f'Mono wavelength {mono_wavelength}')

# ccd configuration

        ccd_config = await ccd.get_configuration()
        chip_x = int(ccd_config['chipWidth'])
        chip_y = int(ccd_config['chipHeight'])

        # core config functions
        await ccd.set_acquisition_format(1, AcquisitionFormat.SPECTRA_IMAGE)
        await ccd.set_region_of_interest(
            1, 0, 0, chip_x, chip_y, 1, chip_y
        )  # Set default ROI, if you want a custom ROI, pass the parameters
        await ccd.set_center_wavelength(mono.id(), mono_wavelength)
        await ccd.set_x_axis_conversion_type(XAxisConversionType.FROM_ICL_SETTINGS_INI)

        await ccd.set_acquisition_count(1)

        exposure_time = 1000 # in ms
        await ccd.set_timer_resolution(TimerResolution.MILLISECONDS)
        await ccd.set_exposure_time(1000)
        await ccd.set_gain(0)  # Least sensitive
        await ccd.set_speed(0)  # Slowest, but least read noise

        raw_data = []

        if await ccd.get_acquisition_ready():
            logger.info('Starting acquisition...')
            await ccd.acquisition_start(open_shutter=True)
            while True:
                try:
                    await asyncio.sleep((exposure_time/1000)*2)
                    raw_data = await ccd.get_acquisition_data()
                    break
                except Exception as e:
                    logger.error(f"Error: {e}")                    
                    logger.info("Data not ready yet...")
        else:
            logger.error("CCD not ready for acquisition, closing...")

        data_wavelength = raw_data
        
        logger.info(f'Data with wavelength: {data_wavelength}')

        wavelengths = data_wavelength['acquisition'][0]['roi'][0]['xData']
        raman_shift = await ccd.raman_convert(wavelengths, excitation_wavelength)
        data_raman_shift = data_wavelength
        data_raman_shift['acquisition'][0]['roi'][0]['xData'][0] = raman_shift

        logger.info(f'Data with raman shift: {data_raman_shift}')

    finally:
        await ccd.close()

    await device_manager.stop()



async def wait_for_mono(mono):
    mono_busy = True
    while mono_busy:
        mono_busy = await mono.is_busy()
        await asyncio.sleep(1)
        logger.info('Mono busy...')


if __name__ == '__main__':
    asyncio.run(main())
