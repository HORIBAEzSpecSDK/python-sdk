# Dependencies: matplotlib package
import asyncio

import matplotlib.pyplot as plt
from loguru import logger

from horiba_sdk.devices.device_manager import DeviceManager


async def main():
    device_manager = DeviceManager(start_icl=True)
    await device_manager.start()

    if not device_manager.spectracq3_devices or not device_manager.monochromators:
        logger.error('Required monochromator or spectracq3 not found')
        await device_manager.stop()
        return

    mono = device_manager.monochromators[0]
    await mono.open()
    await wait_for_mono(mono)
    spectracq3 = device_manager.spectracq3_devices[0]
    await spectracq3.open()
    # await wait_for_saq3(spectracq3)

    start_wavelength = 490
    end_wavelength = 520
    increment_wavelength = 3
    wavelengths = list(range(start_wavelength, end_wavelength + 1, increment_wavelength))
    x_data = []
    y_data_current = []
    y_data_voltage = []
    y_data_counts = []

    try:
        await spectracq3.set_acq_set(1, 0, 1, 0)

        for wavelength in wavelengths:
            await mono.move_to_target_wavelength(wavelength)
            while await mono.is_busy():
                await asyncio.sleep(0.1)
            logger.info(f'Monochromator set to {wavelength}nm')

            # if not await spectracq3.is_busy():

            await spectracq3.acq_start(1)
            await asyncio.sleep(3)
            data = await spectracq3.get_available_data()
            logger.info(f'Acquired data at {wavelength}nm: {data}')
            x_data.append(wavelength)
            y_data_current.append(data[0]['currentSignal']['value'])
            y_data_voltage.append(data[0]['voltageSignal']['value'])
            y_data_counts.append(data[0]['ppdSignal']['value'])

    finally:
        await mono.close()
        await spectracq3.close()
        await device_manager.stop()

    # await plot_values(start_wavelength, end_wavelength, spectrum)
    # if you need to plot voltage or counts, change the y_data_current to y_data_voltage or y_data_counts
    await plot_values(start_wavelength, end_wavelength, x_data, y_data_current)


async def plot_values(start_wavelength, end_wavelength, x_data, y_data):
    # Plotting the data
    plt.plot(x_data, y_data, linestyle='-')
    plt.title(f'Range Scan {start_wavelength}-{end_wavelength}[nm] vs. Intensity')
    plt.xlabel('Wavelength')
    plt.ylabel('Intensity')
    plt.grid(True)
    plt.show()


# async def wait_for_saq3(saq3):
#     acquisition_busy = True
#     while acquisition_busy:
#         acquisition_busy = await saq3.is_busy()
#         await asyncio.sleep(1)
#         logger.info('Acquisition busy')


async def wait_for_mono(mono):
    mono_busy = True
    while mono_busy:
        mono_busy = await mono.is_busy()
        await asyncio.sleep(1)
        logger.info('Mono busy...')


if __name__ == '__main__':
    asyncio.run(main())
