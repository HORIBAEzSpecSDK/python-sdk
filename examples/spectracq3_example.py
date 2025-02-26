import asyncio
import sys

from loguru import logger

from horiba_sdk.devices.device_manager import DeviceManager


async def main():
    """
    Main function to demonstrate the discovery and interaction with SpectrAcq3 devices.

    This example initializes the DeviceManager, discovers SpectrAcq3 devices, retrieves their serial numbers,
    logs the information, and then closes the connections.
    """
    # Initialize the DeviceManager
    device_manager = DeviceManager(enable_logging=True)

    try:
        # Start the DeviceManager
        await device_manager.start()

        # Discover SpectrAcq3 devices
        await device_manager.discover_devices()

        # Iterate over discovered SpectrAcq3 devices
        for spectracq3 in device_manager.spectracq3_devices:
            # Open the device
            await spectracq3.open()

            # Retrieve and log the serial number
            serial_number = await spectracq3.get_serial_number()
            logger.info(f'Discovered SpectrAcq3 with Serial Number: {serial_number}')

            # Close the device
            await spectracq3.close()

    finally:
        # Stop the DeviceManager
        await device_manager.stop()


if __name__ == "__main__":
    # configure the log level from the console to show severity level info and above
    logger.configure(handlers=[{"sink": sys.stdout, "level": "INFO"}])
    asyncio.run(main()) 