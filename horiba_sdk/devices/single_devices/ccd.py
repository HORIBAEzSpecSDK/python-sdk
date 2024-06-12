from types import TracebackType
from typing import Any, Optional, final

from loguru import logger
from overrides import override

from horiba_sdk.communication import AbstractCommunicator, Response
from horiba_sdk.core.acquisition_format import AcquisitionFormat
from horiba_sdk.core.clean_count_mode import CleanCountMode
from horiba_sdk.core.resolution import Resolution
from horiba_sdk.core.timer_resolution import TimerResolution
from horiba_sdk.core.x_axis_conversion_type import XAxisConversionType
from horiba_sdk.icl_error import AbstractErrorDB

from .abstract_device import AbstractDevice


@final
class ChargeCoupledDevice(AbstractDevice):
    """Charge Coupled Device

    This class should not be instanced by the end user. Instead, the :class:`horiba_sdk.devices.DeviceManager`
    should be used to access the detected CCDs on the system.
    """

    def __init__(self, device_id: int, communicator: AbstractCommunicator, error_db: AbstractErrorDB) -> None:
        super().__init__(device_id, communicator, error_db)

    async def __aenter__(self) -> 'ChargeCoupledDevice':
        await self.open()
        self._config: dict[str, Any] = await self.get_configuration()
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
        return response.results['configuration']

    async def get_gain_token(self) -> int:
        """Returns the current gain token.

        .. note:: The CCD can have different sensors installed, which can have different gain values. This is why only
        the token to the gain is returned. You need to first check what gain values are available for the CCD using the
        get_configuration function. Please see the according "Gain and Speed" documentation.

        Returns:
            int: Gain token of the ccd

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getGain', {'index': self._id})
        gain: int = int(response.results['token'])
        return gain

    async def set_gain(self, gain_token: int) -> None:
        """Sets the gain of the CCD.

        .. note:: The CCD can have different sensors installed, which can have different gain values. Therefore you need
        to first check what gain values are available for the CCD using the get_configuration function. Please see the
        according "Gain and Speed" documentation.

        Args:
            gain_token (int): Token of the desired gain

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('ccd_setGain', {'index': self._id, 'token': gain_token})

    async def get_speed_token(self) -> int:
        """Returns the speed token.

        .. note:: The CCD can have different sensors installed, which can have different speed values. This is why only
        the token to the speed is returned. You need to first check what speed values are available for the CCD using
        the get_configuration function. Please see the according "Gain and Speed" documentation.

        Returns:
            int: Speed token of the CCD.

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getSpeed', {'index': self._id})
        speed_token: int = int(response.results['token'])
        return speed_token

    async def set_speed(self, speed_token: int) -> None:
        """Sets the speed of the CCD

        .. note:: The CCD can have different sensors installed, which can have different speed values. Therefore you
        need to first check what speed values are available for the CCD using the get_configuration function. Please
        see the according "Gain and Speed" documentation.

        Args:
            speed_token (int): Token of the desired speed.

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('ccd_setSpeed', {'index': self._id, 'token': speed_token})

    async def get_fit_parameters(self) -> list[int]:
        """Returns the fit parameters of the CCD

        Returns:
            List[int]: Fit parameters

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getFitParams', {'index': self._id})
        fit_params: list[int] = [int(x) for x in response.results['params'].split(',')]
        return fit_params

    async def set_fit_parameters(self, fit_params: list[int]) -> None:
        """Sets the fit parameters of the CCD

        Args:
            fit_params (List[int]): Fit parameters

        Raises:
            Exception: When an error occurred on the device side
        """
        fit_params_str: str = ','.join(map(str, fit_params))
        await super()._execute_command('ccd_setFitParams', {'index': self._id, 'params': fit_params_str})

    async def get_timer_resolution(self) -> TimerResolution:
        """Returns the timer resolution of the CCD in microseconds [μs]

        Returns:
            int: Timer resolution in microseconds [μs]

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getTimerResolution', {'index': self._id})
        timer_resolution: int = int(response.results['resolution'])
        # TODO: this is temporary, as soon as the resolution is returned as 0,1 we can remove this
        if timer_resolution == 1000:
            return TimerResolution._1000_MICROSECONDS
        elif timer_resolution == 1:
            return TimerResolution._1_MICROSECOND
        else:
            raise Exception(f'Unknown timer resolution {timer_resolution}')

    async def set_timer_resolution(self, timer_resolution: TimerResolution) -> None:
        """Sets the timer resolution of the CCD

        .. note:: The timer resolution value of 1 microsecond is not supported by all CCDs.

        Args:
            timer_resolution (int): Timer resolution

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command(
            'ccd_setTimerResolution', {'index': self._id, 'resolution': timer_resolution.value}
        )

    async def set_acquisition_format(self, number_of_rois: int, acquisition_format: AcquisitionFormat) -> None:
        """Sets the acquisition format and the number of ROIs (Regions of Interest) or areas.

        After using this command to set the number of ROIs and format, the set_region_of_interest function
        should be used to define each ROI. Note: The Crop and Fast Kinetics acquisition formats are not
        supported by every CCD.

        Args:
            number_of_rois (int): Number of regions of interest
            acquisition_format (AcquisitionFormat): Acquisition format

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command(
            'ccd_setAcqFormat', {'index': self._id, 'format': acquisition_format.value, 'numberOfRois': number_of_rois}
        )

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
            roi_index (int, optional): One based index of the region of interest. Defaults to 1.
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
        return XAxisConversionType(response.results['type'])

    async def set_acquisition_count(self, count: int) -> None:
        """Sets the number of acquisition measurements to be performed sequentially by the hardware.

        A count > 1 is commonly referred to as "MultiAcq".

        Args:
            count (int): The number of acquisition measurements.
        """
        await super()._execute_command('ccd_setAcqCount', {'index': self._id, 'count': count})

    async def get_acquisition_count(self) -> int:
        """Gets the number of acquisitions to be performed. The acquisition count is used to perform multiple
        acquisitions in a row.
        """
        response: Response = await super()._execute_command('ccd_getAcqCount', {'index': self._id})
        return int(response.results['count'])

    async def get_clean_count(self) -> tuple[int, CleanCountMode]:
        """Gets the clean count mode of the CCD and the according mode"""
        response: Response = await super()._execute_command('ccd_getCleanCount', {'index': self._id})
        count: int = int(response.results['count'])
        mode: CleanCountMode = CleanCountMode(response.results['mode'])
        return count, mode

    async def set_clean_count(self, count: int, mode: CleanCountMode) -> None:
        """Sets the clean count mode of the CCD and the according mode
        Args:
            count (int): The number of acquisitions to be performed.
            mode (CleanCountMode): The mode of the clean count
        """
        await super()._execute_command('ccd_setCleanCount', {'index': self._id, 'count': count, 'mode': mode.value})

    async def get_acquisition_data_size(self) -> int:
        """Returns the size of the acquisition data of the CCD

        Returns:
            int: Size of the data

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getDataSize', {'index': self._id})
        return int(response.results['size'])

    async def get_temperature(self) -> float:
        """Chip temperature of the CCD.

        Returns:
            float: chip's temperature in degree Celsius

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getChipTemperature', {'index': self._id})
        return float(response.results['temperature'])

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

    async def set_exposure_time(self, exposure_time: int) -> None:
        """Sets the exposure time in timer resolution units (1us or 1000us)

        Examples:
        - If exposure_time is set to 50, and the timer resolution value is 1000, the CCD exposure time
          (integration time) = 50 milliseconds.
        - If exposure_time is set to 50, and the timer resolution value is 1, the CCD exposure time
          (integration time) = 50 microseconds.

        Args:
            exposure_time (int): Exposure time in timer resolution units (1us or 1000us)
        Raises:
            Exception: When an error occurred on the device side
        """

        await super()._execute_command('ccd_setExposureTime', {'index': self._id, 'time': exposure_time})

    async def get_trigger_input(self) -> tuple[bool, int, int, int]:
        """This command is used to get the current setting of the input trigger.

        The address, event, and signalType parameters are used to define the input trigger based on the
        supported options of that particular CCD.

        The supported trigger options are retrieved using the get_configuration function, and begin with the
        “Triggers” string contained in the configuration.

        Returns:
            Tuple[bool, int, int, int]:
                enabled: Specifies if the signal is enabled (e.g. False = Disabled),
                address: used to specify where the trigger is located. (e.g. 0 = Trigger Input).
                         Note: Value of -1 indicates that the input trigger is disabled,
                event: used to specify when the trigger event should occur. (e.g. 0 = Once - Start All)
                       Note: Value of -1 indicates that the input trigger is disabled,
                signal type: used to specify how the signal will cause the input trigger. (e.g. 0 = TTL Falling Edge)
                       Note: Value of -1 indicates that the input trigger is disabled,

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getTriggerIn', {'index': self._id})
        address = int(response.results['address'])
        event = int(response.results['event'])
        signal_type = int(response.results['signalType'])
        enabled = address > -1 and event > -1 and signal_type > -1
        return enabled, address, event, signal_type

    async def set_trigger_input(self, enabled: bool, address: int, event: int, signal_type: int) -> None:
        """This command is used to enable or disable the trigger input.

        When enabling the trigger input, the address, event, and signalType parameters are used to define
        the input trigger based on the supported options of that particular CCD.

        The supported trigger options are retrieved using the get_configuration function, and begin with the
        “Triggers” string contained in the configuration.

        Args:
            enabled (bool): Enable or disable the trigger input. Note: When disabling the input trigger,
                            the address, event, and signalType parameters are ignored.
            address (int): Used to specify where the trigger is located. (e.g. 0 = Trigger Input)
            event (int): Used to specify when the trigger event should occur. (e.g. 0 = Once - Start All)
            signal_type (int): Used to specify how the signal will cause the input trigger. (e.g. 0 = TTL Falling Edge)

        Raises:
            Exception: When an error occurred on the device side
        """
        if not enabled:
            address = -1
            event = -1
            signal_type = -1

            await super()._execute_command(
                'ccd_setTriggerIn',
                {'index': self._id, 'enable': enabled, 'address': address, 'event': event, 'signalType': signal_type},
            )
            return

        found_triggers = [trigger for trigger in self._config['Triggers'] if trigger['Token'] == address]
        if not found_triggers:
            raise Exception(f'Trigger address {address} not found in the configuration')

        found_events = [
            trigger_event for trigger_event in found_triggers[0]['Events'] if trigger_event['Token'] == event
        ]
        if not found_events:
            raise Exception(f'Trigger event {event} not found in the configuration')

        found_signal_types = [signal for signal in found_events[0]['Types'] if signal['Token'] == signal_type]
        if not found_signal_types:
            raise Exception(f'Trigger signal type {signal_type} not found in the configuration')

        await super()._execute_command(
            'ccd_setTriggerIn',
            {'index': self._id, 'enable': enabled, 'address': address, 'event': event, 'signalType': signal_type},
        )

    async def get_signal_output(self) -> tuple[bool, int, int, int]:
        """This command is used to get the current setting of the signal output.

        The address, event, and signalType parameters are used to define the signal based on the supported
        options of that particular CCD.

        The supported signal options are retrieved using the get_configuration command, and begin with the
        “Signals” string contained in the configuration.

        Returns:
            Tuple[bool, int, int, int]:
                enabled: Specifies if the signal is enabled (e.g. False = Disabled),
                address: Used to specify where the signal is located (e.g. 0 = Signal Output),
                         Note: Value of -1 indicates that the signal output is disabled,
                event: Used to specify when the signal event should occur. (e.g. 3 = Shutter Open)
                       Note: Value of -1 indicates that the signal output is disabled,
                signal type: how the signal will cause the event. (e.g. 0 = TTL Active High)
                       Note: Value of -1 indicates that the signal output is disabled,

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('ccd_getSignalOut', {'index': self._id})
        address = int(response.results['address'])
        event = int(response.results['event'])
        signal_type = int(response.results['signalType'])
        enabled = address > -1 and event > -1 and signal_type > -1
        return enabled, address, event, signal_type

    async def set_signal_output(self, enabled: bool, address: int, event: int, signal_type: int) -> None:
        """This command is used to enable or disable the signal output.

        When enabling the signal output, the address, event, and signalType parameters are used to
        define the signal based on the supported options of that particular CCD.

        The supported signal options are retrieved using the ccd_getConfig command, and begin with the
        “Signals” string contained in the configuration.

        Args:
            enabled (bool): Enable or disable the signal output. Note: When disabling the signal output,
                            the address, event, and signal_type parameters are ignored.
            address (int): Used to specify where the signal is located (e.g. 0 = Signal Output)
            event (int): Used to specify when the signal event should occur. (e.g. 3 = Shutter Open)
            signal_type (int): How the signal will cause the event. (e.g. 0 = TTL Active High)

        """
        if not enabled:
            address = -1
            event = -1
            signal_type = -1

            await super()._execute_command(
                'ccd_setSignalOut',
                {'index': self._id, 'enable': enabled, 'address': address, 'event': event, 'signalType': signal_type},
            )
            return

        found_triggers = [trigger for trigger in self._config['Signals'] if trigger['Token'] == address]
        if not found_triggers:
            raise Exception(f'Signal address {address} not found in the configuration')

        found_events = [
            trigger_event for trigger_event in found_triggers[0]['Events'] if trigger_event['Token'] == event
        ]
        if not found_events:
            raise Exception(f'Signal event {event} not found in the configuration')

        found_signal_types = [signal for signal in found_events[0]['Types'] if signal['Token'] == signal_type]
        if not found_signal_types:
            raise Exception(f'Signal type {signal_type} not found in the configuration')

        await super()._execute_command(
            'ccd_setSignalOut',
            {'index': self._id, 'enable': enabled, 'address': address, 'event': event, 'signalType': signal_type},
        )

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
        """Starts an acquisition that has been set up according to the previously defined acquisition parameters.

        Note: To specify the acquisiton parameters please see set_region_of_interest, set_x_axis_conversion_type.
        If there are no acquisition parameters set at the time of acquisition it may result in no data being generated.

        Args:
            open_shutter (bool): Whether the shutter of the camera should be open during the acquisition.
        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('ccd_setAcquisitionStart', {'index': self._id, 'openShutter': open_shutter})

    async def get_acquisition_busy(self) -> bool:
        """Returns true if the CCD is busy with the acquisition"""
        response: Response = await super()._execute_command('ccd_getAcquisitionBusy', {'index': self._id})
        return bool(response.results['isBusy'])

    async def set_acquisition_abort(self, reset_port: bool = True) -> None:
        """Stops the acquisition of the CCD"""
        await super()._execute_command('ccd_setAcquisitionAbort', {'index': self._id, 'resetPort': reset_port})

    async def get_acquisition_data(self) -> dict[Any, Any]:
        """Retrieves data from the last acquisition.

        The acquisition description string consists of the following information:
        - acqIndex: Acquisition number
        - roiIndex: Region of Interest number
        - xOrigin: ROI’s X Origin
        - yOrigin: ROI’s Y Origin
        - xSize: ROI’s X Size
        - ySize: ROI’s Y Size
        - xBinning: ROI’s X Bin
        - yBinning: ROI’s Y Bin
        - Timestamp: This is a timestamp that relates to the time when the all the programmed acquisitions have
                     completed. The data from all programmed acquisitions are retrieve from the CCD after all
                     acquisitions have completed, therefore the same timestamp is used for all acquisitions.
        """
        response: Response = await super()._execute_command('ccd_getAcquisitionData', {'index': self._id})
        return response.results['acquisition']
