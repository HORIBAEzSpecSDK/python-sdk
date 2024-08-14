import asyncio

from horiba_sdk.devices.device_manager import DeviceManager


async def main():
    device_manager = DeviceManager(start_icl=True)
    await device_manager.start()

    if not device_manager.charge_coupled_devices:
        print('No CCDs found, exiting...')
        await device_manager.stop()
        return

    async with device_manager.charge_coupled_devices[0] as ccd:
        configuration = await ccd.get_configuration()

    await device_manager.stop()

    print('------ Configuration ------')
    print(f'Gains: {configuration["gains"]}')
    print(f'Speeds: {configuration["speeds"]}')


if __name__ == '__main__':
    asyncio.run(main())
