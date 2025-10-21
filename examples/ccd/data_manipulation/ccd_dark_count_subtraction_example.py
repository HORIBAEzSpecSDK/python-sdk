import asyncio

from loguru import logger

from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.timer_resolution import TimerResolution
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.devices.device_manager import DeviceManager


async def subtract_dark_count(shutter_open_data: list[float], shutter_closed_data: list[float]) -> list[float]:
    values_noise_free = []
    zipped_data = zip(shutter_open_data, shutter_closed_data)
    for data in zipped_data:
        value_noise_free = data[0] - data[1]
        values_noise_free.append(value_noise_free)
    return values_noise_free


async def main():
    device_manager = DeviceManager(start_icl=True)
    await device_manager.start()

    if not device_manager.charge_coupled_devices:
        logger.error('No CCDs found, exiting...')
        await device_manager.stop()
        return

    ccd = device_manager.charge_coupled_devices[0]
    await ccd.open()

    try:
        # ccd configuration

        ccd_config = await ccd.get_configuration()
        chip_x = int(ccd_config['chipWidth'])
        chip_y = int(ccd_config['chipHeight'])

        # core config functions
        await ccd.set_acquisition_format(1, AcquisitionFormat.SPECTRA_IMAGE)
        await ccd.set_region_of_interest(
            1, 0, 0, chip_x, chip_y, 1, chip_y
        )  # Set default ROI, if you want a custom ROI, pass the parameters
        await ccd.set_x_axis_conversion_type(XAxisConversionType.NONE)

        await ccd.set_acquisition_count(1)

        exposure_time = 1000 # in ms
        await ccd.set_timer_resolution(TimerResolution.MILLISECONDS)
        await ccd.set_exposure_time(1000)
        await ccd.set_gain(0)  # Least sensitive
        await ccd.set_speed(0)  # Slowest, but least read noise

        await ccd.set_acquisition_count(1)
        data_shutter_closed = []
        if await ccd.get_acquisition_ready():
            logger.info('Starting acquisition...')
            await ccd.acquisition_start(open_shutter=False)
            while True:
                try:
                    await asyncio.sleep((exposure_time/1000)*2)
                    data_shutter_closed = await ccd.get_acquisition_data()
                    break
                except Exception as e:
                    logger.error(f"Error: {e}")
                    logger.info("Data not ready yet...")
            logger.info(f'Data with closed shutter: {data_shutter_closed}')

        data_shutter_open = []
        if await ccd.get_acquisition_ready():
            logger.info('Starting acquisition...')
            await ccd.acquisition_start(open_shutter=True)
            while True:
                try:
                    await asyncio.sleep((exposure_time/1000)*2)
                    data_shutter_open = await ccd.get_acquisition_data()
                    break
                except Exception as e:
                    logger.error(f"Error: {e}")
                    logger.info("Data not ready yet...")
            logger.info(f'Data with open shutter: {data_shutter_open}')

        data_shutter_open_selected = data_shutter_open['acquisition'][0]['roi'][0]['yData'][0]
        data_shutter_closed_selected = data_shutter_closed['acquisition'][0]['roi'][0]['yData'][0]
        data_without_noise = await subtract_dark_count(data_shutter_open_selected, data_shutter_closed_selected)
        data_subtracted = data_shutter_open
        data_subtracted['acquisition'][0]['roi'][0]['yData'][0] = data_without_noise

        logger.info(f'Data without noise: {data_subtracted}')

    finally:
        await ccd.close()

    await device_manager.stop()


if __name__ == '__main__':
    asyncio.run(main())
