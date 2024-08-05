from enum import Enum
from types import TracebackType
from typing import Any, Optional, final

import pint
from loguru import logger
from overrides import override

from horiba_sdk import ureg
from horiba_sdk.communication import AbstractCommunicator, Response
from horiba_sdk.core.resolution import Resolution
from horiba_sdk.icl_error import AbstractErrorDB

from .abstract_device import AbstractDevice


@final
class ChargeCoupledDevice(AbstractDevice):
    """Charge Coupled Device

    This class should not be instanced by the end user. Instead, the :class:`horiba_sdk.devices.DeviceManager`
    should be used to access the detected CCDs on the system.
    """

    @final
    class Gain(Enum):
        HIGH_LIGHT = 0
        BEST_DYNAMIC_RANGE = 1
        HIGH_SENSITIVITY = 2

    @final
    class Speed(Enum):
        SLOW_45_kHz = 0
        MEDIUM_1_MHz = 1
        FAST_1_MHz_Ultra = 2

    @final
    class AcquisitionFormat(Enum):
        SPECTRA = 0
        IMAGE = 1
        CROP = 2
        FAST_KINETICS = 3

    @final
    class CleanCountMode(Enum):
        Mode1 = 238

    @final
    class XAxisConversionType(Enum):
        """
        Enumeration of possible XAxisConversionTypes
        None = 0, CCD-Firmware = 1, ICL ini settings file = 2
        """

        NONE = 0
        FROM_CCD_FIRMWARE = 1
        FROM_ICL_SETTINGS_INI = 2
    
    @final
    class TimerResolution(Enum):
        """
        .. note:: The timer resolution value of 1 microsecond is not supported by all CCDs.
        """

        MILLISECONDS = 0
        MICROSECONDS = 1

    def __init__(self, device_id: int, communicator: AbstractCommunicator, error_db: AbstractErrorDB) -> None:
        super().__init__(device_id, communicator, error_db)

    async def __aenter__(self) -> 'ChargeCoupledDevice':
        await self.open()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException], exc_value: BaseException, traceback: Optional[TracebackType]
    ) -> None:
        is_open = await self.is_open()
        if not is_open:
            logger.debug('CCD is already closed')
            return

        await self.close()

    @override
    async def open(self) -> None:
        """Opens the connection to the Charge Coupled Device

        Raises:
            Exception: When an error occurred on the device side
        """
        await super().open()
        await super()._execute_command('ccd_open', {'index': self._id})

    @override
    async def close(self) -> None:
        """Closes the connection to the ChargeCoupledDevice

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('ccd_close', {'index': self._id})

    async def is_open(self) -> bool:
        """Checks if the connection to the charge coupled device is open.

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_isOpen', {'index': self._id})
        return bool(response.results['open'])

    async def restart(self) -> None:
        """Restarts the charge coupled device
        This command only works if the camera has been opened before.
        The connection to the camera stays open after the restart.

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('ccd_restart', {'index': self._id})

    async def get_configuration(self) -> dict[str, Any]:
        """Returns the configuration of the CCD

        Returns:
            dict[str, Any]: Configuration of the CCD

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getConfig', {'index': self._id})
        return response.results

    async def get_number_of_averages(self) -> int:
        """Returns the number of averages of the CCD

        Returns:
            int: Number of averages

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getNumberOfAvgs', {'index': self._id})
        return int(response.results['count'])

    async def set_number_of_averages(self, number_of_averages: int) -> None:
        """Sets the number of averages of the CCD

        Args:
            number_of_averages (int): Number of averages

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('ccd_setNumberOfAvgs', {'index': self._id, 'count': number_of_averages})

    async def get_gain(self) -> str:
        """Returns the gain of the CCD

        Returns:
            str: Gain

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getGain', {'index': self._id})
        return str(response.results['info'])

    async def set_gain(self, gain: Gain) -> None:
        """Sets the gain of the CCD

        Args:
            gain (Gain): Gain

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('ccd_setGain', {'index': self._id, 'token': gain.value})

    async def get_speed(self) -> str:
        """Returns the speed of the CCD

        Returns:
            str: Speed

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getSpeed', {'index': self._id})
        return str(response.results['info'])

    async def set_speed(self, speed: Speed) -> None:
        """Sets the speed of the CCD

        Args:
            speed (Speed): Speed

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('ccd_setSpeed', {'index': self._id, 'token': speed.value})

    async def get_fit_params(self) -> str:
        """Returns the fit parameters of the CCD

        Returns:
            str: Fit parameters

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getFitParams', {'index': self._id})
        return str(response.results['params'])

    async def set_fit_params(self, fit_params: str) -> None:
        """Sets the fit parameters of the CCD

        Args:
            fit_params (str): Fit parameters

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('ccd_setFitParams', {'index': self._id, 'params': fit_params})

    async def get_timer_resolution(self) -> int:
        """Returns the timer resolution of the CCD

        Returns:
            int: Timer resolution

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getTimerResolution', {'index': self._id})
        return int(response.results['resolution'])

    async def set_timer_resolution(self, timer_resolution: TimerResolution) -> None:
        """Sets the timer resolution of the CCD

        Args:
            timer_resolution (int): Timer resolution

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('ccd_setTimerResolution', {'index': self._id, 'resolutionToken': timer_resolution.value})

    async def set_acquisition_format(self, number_of_rois: int, acquisition_format: AcquisitionFormat) -> None:
        """Sets the acquisition format and the number of ROIs (Regions of Interest) or areas. After using this command
         to set the number of ROIs and format, the ccd_setRoi command should be used to define each ROI.
         Note: The Crop (2) and Fast Kinetics (3) acquisition formats are not supported by every CCD.

        Args:
            acquisition_format (AcquisitionFormat): Acquisition format
            number_of_rois (int): Number of regions of interest

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command(
            'ccd_setAcqFormat', {'index': self._id, 'format': acquisition_format.value, 'numberOfRois': number_of_rois}
        )

    async def set_x_axis_conversion_type(self, conversion_type: XAxisConversionType) -> None:
        """Sets the X-axis pixel conversion type to be used when retrieving the acquisition data with the
        ccd_getAcquisitionData command.
        0 = None (default)
        1 = CCD FIT parameters contained in the CCD firmware
        2 = Mono Wavelength parameters contained in the icl_settings.ini file

        Args:
            conversion_type (XAxisConversionType): Conversion type Integer. The X-axis pixel conversion type to be used.

        """
        await super()._execute_command('ccd_setXAxisConversionType', {'index': self._id, 'type': conversion_type.value})

    async def get_x_axis_conversion_type(self) -> XAxisConversionType:
        """Gets the conversion type of the x axis.
        0 = None (default)
        1 = CCD FIT parameters contained in the CCD firmware
        2 = Mono Wavelength parameters contained in the icl_settings.ini file
        """
        response: Response = await super()._execute_command('ccd_getXAxisConversionType', {'index': self._id})
        return self.XAxisConversionType(self.XAxisConversionType(response.results['type']))

    async def set_acquisition_count(self, count: int) -> None:
        """Sets the number of acquisitions to be performed. The acquisition count is used to perform multiple
            acquisitions in a row.
        Args:
            count (int): The number of acquisitions to be performed.
        """
        await super()._execute_command('ccd_setAcqCount', {'index': self._id, 'count': count})

    async def get_acquisition_count(self) -> int:
        """Gets the number of acquisitions to be performed. The acquisition count is used to perform multiple
        acquisitions in a row.
        """
        response: Response = await super()._execute_command('ccd_getAcqCount', {'index': self._id})
        return int(response.results['count'])

    async def get_clean_count(self) -> str:
        """Gets the clean count mode of the CCD and the according mode"""
        response: Response = await super()._execute_command('ccd_getCleanCount', {'index': self._id})
        answer: str = 'count: ' + str(response.results['count']) + ' ' + 'mode: ' + str(response.results['mode'])
        return answer

    async def set_clean_count(self, count: int, mode: CleanCountMode) -> None:
        """Sets the clean count mode of the CCD and the according mode
        Args:
            count (int): The number of acquisitions to be performed.
            mode (CleanCountMode): The mode of the clean count
        """
        await super()._execute_command('ccd_setCleanCount', {'index': self._id, 'count': count, 'mode': mode.value})

    async def get_data_size(self) -> int:
        """Returns the size of the data of the CCD

        Returns:
            int: Size of the data

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getDataSize', {'index': self._id})
        return int(response.results['size'])

    async def get_temperature(self) -> pint.Quantity:
        """Chip temperature of the CCD.

        Returns:
            pint.Quantity: chip's temperature in degree Celsius

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getChipTemperature', {'index': self._id})
        return ureg.Quantity(response.results['temperature'], ureg.degC)  # type: ignore

    async def get_chip_size(self) -> Resolution:
        """Chip resolution of the CCD.

        Returns:
            Resolution: chip resolution (width, height)

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getChipSize', {'index': self._id})
        width: int = response.results['x']
        height: int = response.results['y']
        resolution: Resolution = Resolution(width, height)
        return resolution

    async def get_exposure_time(self) -> int:
        """Returns the exposure time in ms

        Returns:
            pint.Quantity: Exposure time in ms
        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getExposureTime', {'index': self._id})
        exposure = int(response.results['time'])
        return exposure

    async def set_exposure_time(self, exposure_time_ms: int) -> None:
        """Sets the exposure time in ms

        Args:
            exposure_time_ms (int): Exposure time in ms
        Raises:
            Exception: When an error occurred on the device side
        """

        await super()._execute_command('ccd_setExposureTime', {'index': self._id, 'time': exposure_time_ms})

    async def get_acquisition_ready(self) -> bool:
        """Returns true if the CCD is ready to acquire

        Returns:
            bool: True if the CCD is ready to acquire
        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getAcquisitionReady', {'index': self._id})
        return bool(response.results['ready'])

    async def set_acquisition_start(self, open_shutter: bool) -> None:
        """Starts the acquisition of the CCD

        Args:
            open_shutter (bool): Whether the shutter of the camera should be open
        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('ccd_setAcquisitionStart', {'index': self._id, 'openShutter': open_shutter})

    async def set_region_of_interest(
        self,
        roi_index: int = 1,
        x_origin: int = 0,
        y_origin: int = 0,
        x_size: int = 1024,
        y_size: int = 256,
        x_bin: int = 1,
        y_bin: int = 256,
    ) -> None:
        """Sets the region of interest of the CCD
        an example json command looks like this:

        Args:
            roi_index (int, optional): Index of the region of interest. Defaults to 1.
            x_origin (int, optional): X origin of the region of interest. Defaults to 0.
            y_origin (int, optional): Y origin of the region of interest. Defaults to 0.
            x_size (int, optional): X size of the region of interest. Defaults to 1024.
            y_size (int, optional): Y size of the region of interest. Defaults to 256.
            x_bin (int, optional): X bin of the region of interest. Defaults to 1.
            y_bin (int, optional): Y bin of the region of interest. Defaults to 256.

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command(
            'ccd_setRoi',
            {
                'index': self._id,
                'roiIndex': roi_index,
                'xOrigin': x_origin,
                'yOrigin': y_origin,
                'xSize': x_size,
                'ySize': y_size,
                'xBin': x_bin,
                'yBin': y_bin,
            },
        )

    async def get_acquisition_data(self) -> dict[Any, Any]:
        """Returns the acquisition data of the CCD
        nina: atm this returns data still formatted for telnet communication, not formatted as json"""
        response: Response = await super()._execute_command('ccd_getAcquisitionData', {'index': self._id})
        return response.results

    async def get_acquisition_busy(self) -> bool:
        """Returns true if the CCD is busy with the acquisition"""
        response: Response = await super()._execute_command('ccd_getAcquisitionBusy', {'index': self._id})
        return bool(response.results['isBusy'])

    async def set_acquisition_abort(self) -> None:
        """Stops the acquisition of the CCD"""
        await super()._execute_command('ccd_setAcquisitionAbort', {'index': self._id})

    ##pb
    async def set_center_wavelength(self, center_wavelength: float) -> None:
        """Sets center wavelength for XAxisConversionType 2"""
        await super()._execute_command('ccd_setCenterWavelength', {'index': self._id, 'wavelength': center_wavelength}, )

    async def pass_command(self, command : str, params = [], values = []) -> None:
        """ command to pass user input strings to ICL"""

        parameters = params
        parameter_values = values

        def convert_to_float(s):
            try:
                float(s)
                return True
            except ValueError:
                return False
        
        j = 0
        for i in parameter_values:
            if convert_to_float(i):
                parameter_values[j] = float(parameter_values[j])
                print(parameter_values[j])
                print(type(parameter_values[j]))
                j += 1
            else:
                j += 1
            
        
        params_dict = dict(zip(parameters, parameter_values))
        params_dict['index'] = self._id


        if params[0] == '':
            response: Response = await super()._execute_command(str(command), {'index' : self._id})
        else:
            response: Response = await super()._execute_command(str(command), params_dict)
            #response : Response = await super()._execute_command(str(command), {'index' : self._id, (parameters[0]): (parameter_values[0])})
        return response
