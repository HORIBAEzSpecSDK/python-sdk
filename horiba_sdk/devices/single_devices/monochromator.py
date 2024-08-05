from enum import Enum
from types import TracebackType
from typing import Optional, final

from loguru import logger
from overrides import override

from horiba_sdk.communication import AbstractCommunicator, Response
from horiba_sdk.icl_error import AbstractErrorDB

from .abstract_device import AbstractDevice


@final
class Monochromator(AbstractDevice):
    """Monochromator device

    This class should not be instanced by the end user. Instead, the :class:`horiba_sdk.devices.DeviceManager`
    should be used to access the detected Monochromators on the system.
    """

    @final
    class ShutterPosition(Enum):
        """Position of the shutter."""

        CLOSED = 0
        OPENED = 1

    @final
    class Grating(Enum):
        """Gratings installed in the monochromator"""

        FIRST = 0
        SECOND = 1
        THIRD = 2

    @final
    class FilterWheelPosition(Enum):
        """Positions of the filter wheel installed in the monochromator.

        .. note:: the filter wheel is an optional module

        """

        # TODO: clarify naming of filter wheel positions
        RED = 0
        GREEN = 1
        BLUE = 2
        YELLOW = 3

    @final
    class Mirror(Enum):
        """Mirrors installed in the monochromator"""

        # TODO: clarify how the mirrors are called
        FIRST = 0
        SECOND = 1

    @final
    class MirrorPosition(Enum):
        """Possible positions of the mirrors"""

        # TODO: clarify what possible position there are
        A = 0
        B = 1

    @final
    class Slit(Enum):
        """Slits available on the monochromator."""

        # TODO: clarify how the slits are called
        A = 0
        B = 1
        C = 2
        D = 3

    @final
    class SlitStepPosition(Enum):
        """Slits steps available on the monochromator."""

        # TODO: clarify how the slits are called
        A = 0
        B = 1
        C = 2
        D = 3

    def __init__(self, device_id: int, communicator: AbstractCommunicator, error_db: AbstractErrorDB) -> None:
        super().__init__(device_id, communicator, error_db)

    async def __aenter__(self) -> 'Monochromator':
        await self.open()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException], exc_value: BaseException, traceback: Optional[TracebackType]
    ) -> None:
        is_open = await self.is_open()
        if not is_open:
            logger.debug('Monochromator is already closed')
            return

        await self.close()

    @override
    async def open(self) -> None:
        """Opens the connection to the Monochromator

        Raises:
            Exception: When an error occured on the device side
        """
        await super().open()
        await super()._execute_command('mono_open', {'index': self._id})

    @override
    async def close(self) -> None:
        """Closes the connection to the Monochromator

        Raises:
            Exception: When an error occured on the device side
        """
        await super()._execute_command('mono_close', {'index': self._id})

    async def is_open(self) -> bool:
        """Checks if the connection to the monochromator is open.

        Raises:
            Exception: When an error occured on the device side
        """
        response: Response = await super()._execute_command('mono_isOpen', {'index': self._id})
        return bool(response.results['open'])

    async def is_busy(self) -> bool:
        """Checks if the monochromator is busy.

        Raises:
            Exception: When an error occured on the device side
        """
        response: Response = await super()._execute_command('mono_isBusy', {'index': self._id})
        return bool(response.results['busy'])

    async def home(self) -> None:
        """Starts the monochromator initialization process called "homing".

        Use :func:`Monochromator.is_busy()` to know if the operation is still taking place.

        Raises:
            Exception: When an error occured on the device side
        """
        await super()._execute_command('mono_init', {'index': self._id})

    async def configuration(self) -> str:
        """Returns the configuration of the monochromator.

        Returns:
            str: configuration of the monochromator
        """
        response: Response = await super()._execute_command('mono_getConfig', {'index': self._id, 'compact': False})
        return str(response.results)

    async def get_current_wavelength(self) -> float:
        """Current wavelength of the monochromator's position in nm.

        Returns:
            float: The current wavelength in nm

        Raises:
            Exception: When an error occurred on the device side
        """
        response = await super()._execute_command('mono_getPosition', {'index': self._id})
        return float(response.results['wavelength'])

    async def calibrate_wavelength(self, wavelength: float) -> None:
        """This command sets the wavelength value of the current grating position of the monochromator.

        .. warning:: This could potentially un-calibrate the monochromator and report an incorrect wavelength
                     compared to the actual output wavelength.

        Args:
            wavelength (float): wavelength in nm

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('mono_setPosition', {'index': self._id, 'wavelength': wavelength})

    async def move_to_target_wavelength(self, wavelength: float) -> None:
        """Orders the monochromator to move to the requested wavelength.

        Use :func:`Monochromator.is_busy()` to know if the operation is still taking place.

        Args:
            wavelength (nm): wavelength

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('mono_moveToPosition', {'index': self._id, 'wavelength': wavelength}, 60)

    async def get_turret_grating(self) -> Grating:
        """Current grating of the turret

        Returns:
            Grating: current grating of turret. See :class:`Monochromator.Grating` for possible values.

        Raises:
            Exception: When an error occured on the device side
        """
        response: Response = await super()._execute_command('mono_getGratingPosition', {'index': self._id})
        return self.Grating(response.results['position'])

    async def set_turret_grating(self, grating: Grating) -> None:
        """Select turret grating

        Args:
            position (Grating): new grating of the turret. See :class:`Monochromator.Grating` for possible values.

        Raises:
            Exception: When an error occured on the device side
        """
        await super()._execute_command('mono_moveGrating', {'index': self._id, 'position': grating.value})

    async def get_filter_wheel_position(self) -> FilterWheelPosition:
        """Current position of the filter wheel.

        Returns:
            FilterWheelPosition: current position of the filter wheel. See :class:`Monochromator.FilterWheelPosition`
            for possible values.

        Raises:
            Exception: When an error occured on the device side
        """
        # TODO: refactor in case there can be more than one filter wheel. What should be done if no filter wheel is
        # installed?
        response: Response = await super()._execute_command(
            'mono_getFilterWheelPosition', {'index': self._id, 'type': 1}
        )
        return self.FilterWheelPosition(response.results['position'])

    async def set_filter_wheel_position(self, position: FilterWheelPosition) -> None:
        """Sets the current position of the filter wheel.

        Returns:
            FilterWheelPosition: current position of the filter wheel. See :class:`Monochromator.FilterWheelPosition`,
            for possible values.

        Raises:
            Exception: When an error occured on the device side
        """
        # TODO: refactor in case there can be more than one filter wheel. What should be done if no filter wheel is
        # installed?
        await super()._execute_command(
            'mono_moveFilterWheel', {'index': self._id, 'type': 1, 'position': position.value}
        )

    async def get_mirror_position(self, mirror: Mirror) -> MirrorPosition:
        """Position of the selected mirror.

        .. todo:: Get more information about possible values and explain elements contained in monochromator at top
           of this class.

        Args:
            mirror (Mirror): desired mirror to get the position from.

        Returns:
            MirrorPosition: current mirror position. See :class:`Monochromator.MirrorPosition` for possible values

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command(
            'mono_getMirrorPosition', {'index': self._id, 'type': mirror.value}
        )
        return self.MirrorPosition(response.results['position'])

    async def set_mirror_position(self, mirror: Mirror, position: MirrorPosition) -> None:
        """Sets the position of the selected mirror.

        .. todo:: Get more information about possible values and explain elements contained in monochromator at top
           of this class.

        Args:
            mirror (Mirror): desired mirror to set the position.
            position (MirrorPosition): position to set. See :class:`Monochromator.MirrorPosition` for possible values

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command(
            'mono_moveMirror', {'index': self._id, 'type': mirror.value, 'position': position.value}
        )

    async def get_slit_position_in_mm(self, slit: Slit) -> float:
        """Returns the position in millimeters [mm] of the selected slit.

        .. todo:: Get more information about possible values and explain elements contained in monochromator at top
           of this class.

        Args:
            slit (Slit): desired slit to get the position from. See :class:`Monochromator.Slit` for possible
            values
        Returns:
            float: position in mm

        Raises:
            Exception: When an error occurred on the device side
        """

        response: Response = await super()._execute_command(
            'mono_getSlitPositionInMM', {'index': self._id, 'type': slit.value}
        )
        return float(response.results['position'])

    async def set_slit_position(self, slit: Slit, position_in_mm: float) -> None:
        """Sets the position of the selected slit.

        .. todo:: Get more information about possible values and explain elements contained in monochromator at top
           of this class.

        Args:
            slit (Slit): desired slit to set the position. See :class:`Monochromator.Slit` for possible values.
            position (float): position to set in millimeters [mm].

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command(
            'mono_moveSlitMM', {'index': self._id, 'type': slit.value, 'position': position_in_mm}
        )

    async def get_slit_step_position(self, slit: Slit) -> SlitStepPosition:
        """Returns the step position of the selected slit.

        .. todo:: Get more information about possible values and explain elements contained in monochromator at top
           of this class.

        Args:
            slit (Slit): desired slit to get the position from. See :class:`Monochromator.Slit` for possible
            values
        Returns:
            SlitStepPosition: step position. See :class:`Monochromator.SlitStepPosition` for possible values

        Raises:
            Exception: When an error occurred on the device side
        """

        response: Response = await super()._execute_command(
            'mono_getSlitStepPosition', {'index': self._id, 'type': slit.value}
        )
        return self.SlitStepPosition(response.results['position'])

    async def set_slit_step_position(self, slit: Slit, step_position: SlitStepPosition) -> None:
        """Sets the step position of the selected slit.

        .. todo:: Get more information about possible values and explain elements contained in monochromator at top
           of this class.

        Args:
            slit (Slit): desired slit to set the step position. See :class:`Monochromator.Slit` for possible values.
            step_position (SlitStepPosition): the step position. See :class:`Monochromator.SlitStepPosition` for
            possible values

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command(
            'mono_moveSlit', {'index': self._id, 'type': slit.value, 'position': step_position.value}
        )

    async def open_shutter(self) -> None:
        """Opens the shutter.

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('mono_shutterOpen', {'index': self._id})

    async def close_shutter(self) -> None:
        """Closes the shutter.

        Raises:
            Exception: When an error occurred on the device side
        """
        await super()._execute_command('mono_shutterClose', {'index': self._id})

    async def get_shutter_position(self) -> ShutterPosition:
        """Returns the shutter position.

        Returns:
            ShutterPosition: OPEN or CLOSED

        Raises:
            Exception: When an error occurred on the device side
        """
        response: Response = await super()._execute_command('mono_getShutterStatus', {'index': self._id})
        return self.ShutterPosition(response.results['position'])

    ##pb
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