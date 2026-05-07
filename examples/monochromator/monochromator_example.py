import asyncio

from loguru import logger

from horiba_sdk.devices.device_manager import DeviceManager


async def main():
    device_manager = DeviceManager(start_icl=True)
    await device_manager.start()

    if not device_manager.monochromators:
        logger.error('No monochromators found, exiting...')
        await device_manager.stop()
        return

    mono = device_manager.monochromators[0]
    await mono.open()
    logger.info(await mono.get_current_wavelength())
    await mono.move_to_target_wavelength(550)
    await wait_for_mono(mono)

    await mono.calibrate_wavelength(100)
    await wait_for_mono(mono)

    logger.warning(await mono.get_current_wavelength())


    await mono.move_to_target_wavelength(100)
    await wait_for_mono(mono)

    logger.warning(await mono.get_current_wavelength())

    await mono.close()

    await device_manager.stop()


async def wait_for_mono(mono):
    mono_is_busy = True
    while mono_is_busy:
        await asyncio.sleep(0.1)
        mono_is_busy = await mono.is_busy()


if __name__ == '__main__':
    asyncio.run(main())
