from abc import ABC, abstractmethod
from typing import Any, List, Optional

from horiba_sdk.communication import AbstractCommunicator, Command, Response
from horiba_sdk.icl_error import AbstractError, AbstractErrorDB


class AbstractDevice(ABC):
    """
    Abstract base class representing a generic device.

    This class provides an interface for device-specific operations. Concrete implementations should provide specific
    functionalities for each of the abstract methods.

    Attributes:
        _id (int):
        _communicator (WebsocketCommunicator):
    """

    def __init__(self, device_id: int, communicator: AbstractCommunicator, error_db: AbstractErrorDB) -> None:
        self._id: int = device_id
        self._error_db: AbstractErrorDB = error_db
        self._communicator: AbstractCommunicator = communicator

    def id(self) -> int:
        """Return the ID of the device.

        Returns:
            int: ID of the device.
        """
        return self._id

    @abstractmethod
    async def open(self) -> None:
        """
        Open a connection to the device.

        Returns:
            Result: Result object indicating success or failure.
        """
        if not self._communicator.opened():
            await self._communicator.open()

    @abstractmethod
    async def close(self) -> None:
        """
        Close the connection to the device.

        Returns:
            Result: Result object indicating success or failure.
        """
        pass

    async def pass_command(
        self, command: str, params: Optional[List[Any]] = None, values: Optional[List[Any]] = None
    ) -> Response:
        """command to pass user input strings to ICL

        .. note: used for internal usage
        """

        parameters = params if params else []
        parameter_values = values if values else []

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
            response: Response = await self._execute_command(str(command), {'index': self._id})
        else:
            response: Response = await self._execute_command(str(command), params_dict)
        return response

    async def _execute_command(self, command_name: str, parameters: dict[Any, Any], timeout: int = 5) -> Response:
        """
        Creates a command from the command name, and it's parameters
        Executes a command and handles the response.

        Args:
            command_name (str): The name of the command to execute.
            parameters (dict): The parameters for the command.

        Returns:
            Response: The response from the device.

        Raises:
            Exception: When an error occurred on the device side.
        """
        response: Response = await self._communicator.request_with_response(
            Command(command_name, parameters), timeout=timeout
        )
        if response.errors:
            self._handle_errors(response.errors)
        return response

    def _handle_errors(self, errors: list[str]) -> None:
        """
        Handles errors, logs them, and may take corrective actions.

        Args:
            errors (Exception): The exception or error to handle.
        """
        for error in errors:
            icl_error: AbstractError = self._error_db.error_from(error)
            icl_error.log()
            # TODO: [saga] only throw depending on the log level, tbd
            raise Exception(f'Error from the ICL: {icl_error.message()}')
