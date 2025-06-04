import asyncio
import time

from loguru import logger

from examples.helpers.save_data_to_disk import save_spectracq3_data_to_csv
from horiba_sdk.devices.device_manager import DeviceManager


async def main():
    device_manager = DeviceManager(start_icl=True)
    await device_manager.start(False)

    if not device_manager.monochromators:
        logger.error('No monochromators found, exiting...')
        await device_manager.stop()
        return

    if not device_manager.spectracq3_devices:
        logger.error('No SpectrAcq3 devices found, exiting...')
        await device_manager.stop()
        return

    mono = device_manager.monochromators[0]
    spectracq3 = device_manager.spectracq3_devices[0]

    await mono.open()
    await spectracq3.open()

    wavelengths = [500, 501, 502]

    try:
        data = []
        for wavelength in wavelengths:
            await mono.move_to_target_wavelength(wavelength)
            while await mono.is_busy():
                await asyncio.sleep(0.1)
            end_timeout = time.time() + 10
            while time.time() < end_timeout:
                if not await spectracq3.is_busy():
                    break
                logger.info('Waiting for SpectrAcq3 to be ready...')
                await asyncio.sleep(0.1)
            logger.info(f'Monochromator set to {wavelength}nm')

            await spectracq3.set_acq_set(1, 0, 1, 0)
            while time.time() < end_timeout:
                if not await spectracq3.is_busy():
                    logger.info(f'SpectrAcq3 is busy:{await spectracq3.is_busy()} ')
                    break
                logger.info('Waiting for SpectrAcq3 to be ready...')
                await asyncio.sleep(0.1)
            await spectracq3.acq_start(1)
            await asyncio.sleep(3)
            spectracq3_data = await spectracq3.get_available_data()
            logger.info(f'Acquired data at {wavelength}nm: {spectracq3_data}')
            spectracq3_data[0]['wavelength'] = wavelength
            data.append(spectracq3_data[0])
        file_name = 'acquisition_data_' + str(wavelengths[0]) + 'nm_' + str(wavelengths[-1]) + 'nm.csv'
        save_spectracq3_data_to_csv(data, file_name)

    finally:
        await mono.close()
        await spectracq3.close()
        await device_manager.stop()


if __name__ == '__main__':
    asyncio.run(main())
