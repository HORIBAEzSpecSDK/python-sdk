import asyncio
import json

from loguru import logger

from horiba_sdk.devices.device_manager import DeviceManager


async def main():
    device_manager = DeviceManager(start_icl=True)
    await device_manager.start()

    if not device_manager.charge_coupled_devices:
        logger.error('Required ccd not found')
        await device_manager.stop()
        return

    ccd = device_manager.charge_coupled_devices[0]
    await ccd.open()
    await wait_for_ccd(ccd)

    try:
        ccd_config = await ccd.get_configuration()
        logger.info(f"CCD triggers: {json.dumps(ccd_config['triggers'], indent=2)}")
        # The values of the "token" fields belonging to the address, event and signal type will be the ones that you
        # have to put in the function below:
        await ccd.set_trigger_input(True, 0, 0, 0)

    finally:
        await ccd.close()

    await device_manager.stop()


async def wait_for_ccd(ccd):
    acquisition_busy = True
    while acquisition_busy:
        acquisition_busy = await ccd.get_acquisition_busy()
        await asyncio.sleep(1)
        logger.info('Acquisition busy')


if __name__ == '__main__':
    asyncio.run(main())
