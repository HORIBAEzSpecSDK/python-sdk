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

    async with device_manager.monochromators[0] as mono:
        logger.info(await mono.get_current_wavelength())
        # TODO: this is currently making the mono be stuck endlessly
        # await mono.move_to_target_wavelength(100)
        mono_is_busy = True
        while mono_is_busy:
            await asyncio.sleep(0.1)
            mono_is_busy = await mono.is_busy()
        logger.warning(await mono.get_current_wavelength())

    await device_manager.stop()


if __name__ == '__main__':
    asyncio.run(main())
