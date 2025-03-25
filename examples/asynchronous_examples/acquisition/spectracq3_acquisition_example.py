import asyncio
import json
from loguru import logger
from horiba_sdk.devices.device_manager import DeviceManager
from examples.asynchronous_examples.other.save_data_to_disk import save_acquisition_data_to_csv  # Assuming the function is in save_data_to_disk.py

async def main():
    device_manager = DeviceManager(start_icl=True)
    await device_manager.start()

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
    all_data = []

    try:
        for wavelength in wavelengths:
            await mono.move_to_target_wavelength(wavelength)
            while await mono.is_busy():
                await asyncio.sleep(0.1)
            logger.info(f'Monochromator set to {wavelength}nm')

            if not await spectracq3.is_busy():

                await spectracq3.set_acq_set(1,0,1,0)
                await spectracq3.acq_start(1)
                while await spectracq3.is_busy():
                    await asyncio.sleep(0.1)
                data = await spectracq3.get_available_data()
                all_data.append(data)
                logger.info(f'Acquired data at {wavelength}nm: {data}')
            else:
                logger.error('SpectrAcq3 not ready for acquisition')

        # Save all data to CSV
        json_data = json.dumps({"acquisition": all_data})
        save_acquisition_data_to_csv(json_data, 'acquisition_data.csv')

    finally:
        await mono.close()
        await spectracq3.close()
        await device_manager.stop()

if __name__ == '__main__':
    asyncio.run(main())
